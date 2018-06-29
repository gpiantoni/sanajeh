from nibabel import load as nload
from nibabel import Nifti1Image

from bidso.files import file_Core


def simulate_anat(root, task_anat, t1):
    mri = nload(str(t1))
    x = mri.get_data()
    nifti = Nifti1Image(x, mri.affine)

    anat_path = task_anat.get_filename(root)
    anat_path.parent.mkdir(exist_ok=True, parents=True)
    nifti.to_filename(str(anat_path))

    return file_Core(anat_path)  # use the general file_Core (Task needs events.tsv)
