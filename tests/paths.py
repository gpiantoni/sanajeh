from pathlib import Path
from shutil import rmtree

TESTS_DIR = Path(__file__).parent
SIMULATED_DIR = TESTS_DIR / 'simulated'

rmtree(SIMULATED_DIR)
SIMULATED_DIR.mkdir()
