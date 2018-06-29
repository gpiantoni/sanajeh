"""BIDS infrastructure
"""
from json import dump

from .files import subject


def simulate_bids(ROOT_PATH):

    participants_tsv = ROOT_PATH / 'participants.tsv'
    with participants_tsv.open('w') as f:
        f.write('participant_id\tage\tsex\n')

        f.write(f'{subject}\t30\tF\n')

    d = {
        "Name": "Dataset with simulated data",
        "BIDSVersion": "1.1",
        "Authors": ["Giovanni Piantoni", ],
        }

    with (ROOT_PATH / 'dataset_description.json').open('w') as f:
        dump(d, f, ensure_ascii=False, indent=' ')
