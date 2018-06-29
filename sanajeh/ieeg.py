from json import dump
from datetime import datetime
from shutil import copyfile
from numpy import ones, r_, arange
from numpy import random

from wonambi import Data

from bidso.objects import Electrodes, iEEG
from bidso.utils import replace_underscore, replace_extension, bids_mkdir

from .data import data_elec
from .fmri import create_events


S_FREQ = 256
DURATION = 192
AMPLITUDE = 1000
EFFECT_SIZE = 2
block_dur = 32
EXTRA_CHANS = ['EOG1', 'EOG2', 'ECG', 'EMG', 'other']

BV_ORIENTATION = 'MULTIPLEXED'  # 'F'
BV_DATATYPE = 'IEEE_FLOAT_32'  # float32
RESOLUTION = 1

fake_time = datetime(2017, 5, 16, 20, 45, 6)


def simulate_ieeg(root, ieeg_task, elec):
    bids_mkdir(root, ieeg_task)

    chan_names = [x['name'] for x in elec]
    ieeg_file = ieeg_task.get_filename(root)

    create_ieeg_data(ieeg_file, chan_names)
    create_ieeg_info(replace_extension(ieeg_file, '.json'))
    create_channels(replace_underscore(ieeg_file, 'channels.tsv'), elec)
    create_events(replace_underscore(ieeg_file, 'events.tsv'))

    return iEEG(ieeg_file)


def simulate_electrodes(root, elec_obj, electrodes_file=None):
    bids_mkdir(root, elec_obj)

    if electrodes_file is None:
        electrodes_file = data_elec
    output_file = elec_obj.get_filename(root)
    copyfile(electrodes_file, output_file)

    coordsystem_file = replace_underscore(output_file, 'coordsystem.json')
    COORDSYSTEM = {
        "iEEGCoordinateSystem": 'T1w',
        "iEEGCoordinateUnits": 'mm',
        "iEEGCoordinateProcessingDescription": "none",
        "IntendedFor": "/sub-bert/ses-day01/anat/sub-bert_ses-day01_acq-wholebrain_T1w.nii.gz",
        "AssociatedImageCoordinateSystem": "T1w",
        "AssociatedImageCoordinateUnits": "mm",
        }

    with coordsystem_file.open('w') as f:
        dump(COORDSYSTEM, f, indent=' ')

    return Electrodes(output_file)


def create_ieeg_data(output_file, elecs):

    n_chan = len(elecs) + len(EXTRA_CHANS)

    random.seed(100)
    t = r_[ones(block_dur * S_FREQ) * EFFECT_SIZE, ones(block_dur * S_FREQ), ones(block_dur * S_FREQ) * EFFECT_SIZE, ones(block_dur * S_FREQ), ones(block_dur * S_FREQ) * EFFECT_SIZE, ones(block_dur * S_FREQ)]
    dat = random.random((n_chan, S_FREQ * DURATION)) * t[None, :] * AMPLITUDE

    data = Data(dat, S_FREQ, chan=elecs + EXTRA_CHANS, time=arange(dat.shape[1]) / S_FREQ)
    data.start_time = fake_time
    data.export(output_file, 'bids')


def create_channels(output_file, elec):
    with output_file.open('w') as f:
        f.write('name\ttype\tunits\tsampling_frequency\tlow_cutoff\thigh_cutoff\tnotch\treference\tstatus\n')
        for one_elec in elec:
            f.write(f'{one_elec["name"]}\tECOG\tµV\t{S_FREQ}\tn/a\tn/a\tn/a\tn/a\tgood\n')

        for chan_name in EXTRA_CHANS:
            f.write(f'{chan_name}\tother\tµV\t{S_FREQ}\tn/a\tn/a\tn/a\tn/a\tgood\n')


def create_ieeg_info(output_file):
    """Use only required fields
    """
    dataset_info = {
        "TaskName": "block",
        "Manufacturer": "simulated",
        "PowerLineFrequency": 50,
    }

    with output_file.open('w') as f:
        dump(dataset_info, f, indent=' ')
