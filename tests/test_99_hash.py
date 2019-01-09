from .paths import HASH_PATH, SIMULATED_DIR
from sanajeh.utils import compute_md5, read_hash


def test_files_on_disk():
    md5_dict = read_hash(SIMULATED_DIR, HASH_PATH)

    for p in sorted(SIMULATED_DIR.rglob('*')):
        if p.is_file():
            filename = str(p.relative_to(SIMULATED_DIR))
            if filename not in md5_dict:
                raise ValueError(f'{filename} not in the md5 list')

            elif compute_md5(p) != md5_dict.pop(filename):
                x = p.open('rb').read(100)
                raise ValueError(f'hash of {filename} does not match stored value\n{x}')

    for filename in md5_dict.keys():
        raise ValueError(f'{filename} in the md5 list but not on disk')
