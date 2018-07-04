"""Remember to update setup.py to include the dataset into pip
"""
from pathlib import Path


ROOT_DIR = Path(__file__).parent

ANAT_DIR = ROOT_DIR / 'data' / 'anat'
data_t1 = ANAT_DIR / 'T1.mgz'
data_aparc = ANAT_DIR / 'aparc.a2009s+aseg.mgz'
data_elec = ROOT_DIR / 'data' / 'electrodes.tsv'
