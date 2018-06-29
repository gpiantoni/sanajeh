from hashlib import md5
from logging import getLogger

from .paths import HASH_PATH, SIMULATED_DIR

lg = getLogger()


def test_files_on_disk(bids_path=SIMULATED_DIR):
    md5_dict = read_hash(bids_path)

    for p in sorted(bids_path.rglob('*')):
        if p.is_file():
            filename = str(p.relative_to(bids_path))
            if filename not in md5_dict:
                lg.warning(f'{filename} not in the md5 list')

            elif compute_md5(p) != md5_dict.pop(filename):
                lg.warning(f'hash of {filename} does not match stored value')

    for filename in md5_dict.keys():
        lg.warning(f'{filename} in the md5 list but not on disk')


def read_hash(bids_path=SIMULATED_DIR):

    md5_dict = {}
    with HASH_PATH.open('r') as f:

        for l in f:
            filename, md5_value = l.strip().split('\t')
            md5_dict[filename] = md5_value

    return md5_dict


def write_hash(bids_path=SIMULATED_DIR):

    with HASH_PATH.open('w') as f:
        for p in sorted(bids_path.rglob('*')):
            if p.is_file():
                f.write(f'{p.relative_to(bids_path)}\t{compute_md5(p)}\n')


def compute_md5(p):
    md5_ = md5()
    with p.open('rb') as f:
        md5_.update(f.read())
        md5_hex = md5_.hexdigest()
    return md5_hex
