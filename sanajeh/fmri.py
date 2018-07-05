from json import dump
from numpy import ones, r_, random, zeros, sum, where
from skimage.transform import downscale_local_mean

from nibabel import Nifti1Image
from nibabel import load as nload

from bidso.objects import Task
from bidso.utils import replace_extension, replace_underscore, bids_mkdir

from .data import data_aparc

TR = 2.


def simulate_bold(root, task_fmri):
    bids_mkdir(root, task_fmri)

    fmri_file = task_fmri.get_filename(root)
    SHIFT = 3
    x = r_[ones(SHIFT), ones(16) * 5, ones(16), ones(16) * 5, ones(16), ones(16) * 5, ones(16 - SHIFT)]

    create_bold(fmri_file, task_fmri.task, 11129, x)

    create_events(replace_underscore(fmri_file, 'events.tsv'))

    return Task(fmri_file)


def create_bold(bold_file, taskname, region_idx, timeseries):

    aparc = nload(str(data_aparc))

    brain = select_region(aparc, lambda x: x > 0)
    act = select_region(aparc, lambda x: x == region_idx)

    t = timeseries.shape[0]

    random.seed(100)
    idx = where(brain.get_data() == 1)
    r = random.randn(idx[0].shape[0], t)

    bold = zeros(brain.get_data().shape + (t, ))
    bold[act.get_data() == 1, :] = timeseries
    bold[idx] += r

    nifti = Nifti1Image(bold.astype('float32'), brain.affine)
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


def select_region(img, func, ratio=4):
    nii = img.get_data()
    selected = zeros(nii.shape)
    selected[func(nii)] = 1

    return downsample(selected, img.affine, ratio)


def downsample(dat, affine, ratio, MIN=0.25):

    dat = downscale_local_mean(dat, (ratio, ratio, ratio))
    dat[dat > MIN] = 1
    dat[dat <= MIN] = 0
    af = affine.copy()
    af[:3, :3] *= ratio
    af[:3, 3] += sum(affine[:3, :3], axis=1) * (ratio / 2 - 1 / 2)

    return Nifti1Image(dat, af)
