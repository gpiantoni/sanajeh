from shutil import rmtree

from sanajeh import simulate_all

from .paths import SIMULATED_DIR


def test_simulate_all():

    rmtree(SIMULATED_DIR, ignore_errors=True)
    SIMULATED_DIR.mkdir()

    simulate_all(SIMULATED_DIR)
