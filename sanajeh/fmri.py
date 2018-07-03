from json import dump
from numpy import array, NaN, ones, r_, stack, random
from scipy.ndimage import geometric_transform

from nibabel import Nifti1Image
from nibabel import load as nload

from bidso.objects import Task
from bidso.utils import replace_extension, replace_underscore, bids_mkdir


def simulate_bold(root, task_fmri, t1):
    bids_mkdir(root, task_fmri)
    mri = nload(str(t1))

    fmri_file = task_fmri.get_filename(root)
    create_bold(mri, fmri_file, task_fmri.task)
    create_events(replace_underscore(fmri_file, 'events.tsv'))

    return Task(fmri_file)


def create_bold(mri, bold_file, taskname):
    x = mri.get_data()
    DOWNSAMPLE = 4

    af = mri.affine.copy()
    af[:3, :3] *= DOWNSAMPLE   # TODO: these should be some translation as well

    xm = stack([x[i::DOWNSAMPLE, i::DOWNSAMPLE, i::DOWNSAMPLE] for i in range(DOWNSAMPLE)], axis=-1).mean(axis=-1)
    xm[xm == 0] = NaN

    # TODO: nicer time series
    SHIFT = 3
    bold = (xm[:, :, :, None] + r_[ones(SHIFT), ones(16) * 5, ones(16), ones(16) * 5, ones(16), ones(16) * 5, ones(16 - SHIFT)])

    TR = 2.

    random.seed(100)
    bold += random.random(bold.shape) * 2
    nifti = Nifti1Image(bold.astype('float32'), af)
    nifti.header['pixdim'][4] = TR
    nifti.header.set_xyzt_units('mm', 'sec')
    nifti.to_filename(str(bold_file))

    d = {
        'RepetitionTime': TR,
        'TaskName': taskname,
        }

    json_bold = replace_extension(bold_file, '.json')
    with json_bold.open('w') as f:
        dump(d, f, ensure_ascii=False, indent=' ')


def create_events(tsv_file):

    DUR = 32
    with tsv_file.open('w') as f:
        f.write('onset\tduration\ttrial_type\n')
        is_move = True
        for i in range(6):
            trial_type = 'move' if is_move else 'rest'
            is_move = not is_move
            f.write(f'{i * DUR}\t{DUR}\t{trial_type}\n')


def todo():
    img = nload('/home/gio/tools/freesurfer/subjects/bert/mri/aparc.a2009s+aseg.mgz')
    nii = img.get_data()
    brain = zeros(nii.shape)
    brain[nii > 111000] = 1
    brain = downsample(brain, img.affine, 4)

    act = zeros(nii.shape)
    index_a2009s = 11129  # ctx_lh_G_precentral
    act[nii == index_a2009s] = 1
    act = downsample(act, img.affine, 4)


def downsample(dat, affine, ratio, MIN=0.5):

    dat = geometric_transform(dat, lambda x: x * ratio)
    dat[dat > MIN] = 1
    dat[dat <= MIN] = 0
    af = affine.copy()
    af[:3, :3] *= ratio
    af[:3, 3] += sum(affine[:3, :3], axis=1) * (ratio / 2 - 1 / 2)

    ix, iy, iz = array(dat.shape) // ratio
    return Nifti1Image(dat[:ix, :iy, :iz], af)
