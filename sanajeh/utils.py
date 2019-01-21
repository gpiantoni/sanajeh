from hashlib import md5
from numpy import load
from wonambi import Dataset
import gzip


def compare_hash_files(simulated_dir, hash_path, skip=None, skip_hidden=True):

    if skip is None:
        skip = []

    md5_dict = read_hash(simulated_dir, hash_path)

    for p in sorted(simulated_dir.rglob('*')):
        if p.is_file():
            if skip_hidden and p.name.startswith('.'):
                continue

            filename = str(p.relative_to(simulated_dir))

            if filename in skip:
                md5_dict.pop(filename)
                continue

            if filename not in md5_dict:
                raise ValueError(f'{filename} not in the md5 list')

            elif compute_md5(p) != md5_dict.pop(filename):
                with p.open('rb') as f:
                    x = f.read(100)
                raise ValueError(f'hash of {filename} does not match stored value\nFile on disk starts with:\n{x}...')

    for filename in md5_dict.keys():
        raise ValueError(f'{filename} in the md5 list but not on disk')


def compute_md5(p):
    """Compute m5sum for a file. If the file is .gz (in the case of .nii.gz)
    then it reads the archived version (the .gz contains metadata that changes
    every time)
    """
    md5_ = md5()

    if p.suffix == '.gz':
        f = gzip.open(p, 'rb')
        val = f.read()

    elif p.suffix == '.vhdr':
        # skip first two lines because it contains the time the file was written
        f = p.open('rb')
        val = b'\n'.join(f.read().split(b'\n')[2:])

    elif p.suffix == '.eeg':
        f = None
        val = Dataset(p).read_data().data[0].astype(int).tobytes()

    elif p.suffix == '.npy':
        f = None
        val = load(p).tobytes()

    else:
        f = p.open('rb')
        val = f.read()

    md5_.update(val)
    if f is not None:
        f.close()

    return md5_.hexdigest()


def read_hash(bids_path, md5_file):

    md5_dict = {}
    with md5_file.open('r') as f:

        for l in f:
            filename, md5_value = l.strip().split('\t')
            md5_dict[filename] = md5_value

    return md5_dict


def write_hash(bids_path, md5_file):

    with md5_file.open('w') as f:
        for p in sorted(bids_path.rglob('*')):
            if p.is_file():
                f.write(f'{p.relative_to(bids_path)}\t{compute_md5(p)}\n')
