from bidso.utils import read_tsv

from .anat import simulate_anat
from .fmri import simulate_bold
from .ieeg import simulate_ieeg
from .files import task_anat, task_fmri, task_ieeg
from .data import data_t1, elec_t1


def simulate_all(ROOT_DIR):
    elec = read_tsv(elec_t1)
    simulate_ieeg(ROOT_DIR, task_ieeg, elec)
    simulate_bold(ROOT_DIR, task_fmri, data_t1)
    simulate_anat(ROOT_DIR, task_anat, data_t1)
