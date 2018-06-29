from .anat import simulate_anat
from .fmri import simulate_bold
from .ieeg import simulate_ieeg, simulate_electrodes
from .pipeline import simulate_all

from pathlib import Path
with (Path(__file__).parent / 'VERSION').open() as f:
    __version__ = f.read().strip()
