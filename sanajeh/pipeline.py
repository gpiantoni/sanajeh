from bidso.utils import read_tsv

from .bids import simulate_bids
from .anat import simulate_anat
from .fmri import simulate_bold
from .ieeg import simulate_ieeg, simulate_electrodes
from .simulate_prf import simulate_prf
from .files import task_anat, task_fmri, task_ieeg, elec_ct, task_prf
from .data import data_t1, data_aparc, data_elec


def simulate_all(ROOT_DIR):
    simulate_bids(ROOT_DIR)

    elec = read_tsv(data_elec)
    simulate_ieeg(ROOT_DIR, task_ieeg, elec)
    simulate_electrodes(ROOT_DIR, elec_ct)
    simulate_bold(ROOT_DIR, task_fmri, data_aparc)
    simulate_anat(ROOT_DIR, task_anat, data_t1)
    simulate_prf(ROOT_DIR, task_prf)
