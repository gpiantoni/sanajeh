from .paths import HASH_PATH, SIMULATED_DIR
from sanajeh.utils import compare_hash_files


def test_files_on_disk():
    compare_hash_files(SIMULATED_DIR, HASH_PATH)
