from json import dump
from textwrap import dedent
from datetime import datetime
from shutil import copyfile
from pathlib import Path
from numpy import ones, memmap, r_
from numpy import random

import bidso

from bidso.objects import Electrodes, iEEG
from bidso.utils import replace_underscore, replace_extension, bids_mkdir
from .fmri import create_events


DATA_PATH = Path(__file__).resolve().parent / 'data'

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
        electrodes_file = DATA_PATH / 'electrodes.tsv'
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

    _write_vhdr(output_file.with_suffix('.vhdr'), elecs + EXTRA_CHANS)
    _write_vmrk(output_file.with_suffix('.vmrk'))

    n_chan = len(elecs) + len(EXTRA_CHANS)

    random.seed(100)
    t = r_[ones(block_dur * S_FREQ) * EFFECT_SIZE, ones(block_dur * S_FREQ), ones(block_dur * S_FREQ) * EFFECT_SIZE, ones(block_dur * S_FREQ), ones(block_dur * S_FREQ) * EFFECT_SIZE, ones(block_dur * S_FREQ)]
    data = random.random((n_chan, S_FREQ * DURATION)) * t[None, :] * AMPLITUDE

    dtype = 'float32'
    memshape = (n_chan, S_FREQ * DURATION)
    mem = memmap(str(output_file), dtype, mode='w+', shape=memshape, order='F')
    mem[:, :] = data
    mem.flush()


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


def _write_vhdr(filename, chans):
    vhdr_txt = f"""\
    Brain Vision Data Exchange Header File Version 1.0
    ; Data created by the BIDSO {bidso.__version__} on {fake_time}

    [Common Infos]
    Codepage=UTF-8
    DataFile={filename.stem}.eeg
    MarkerFile={filename.stem}.vmrk
    DataFormat=BINARY
    ; Data orientation: MULTIPLEXED=ch1,pt1, ch2,pt1 ...
    DataOrientation={BV_ORIENTATION}
    NumberOfChannels={len(chans)}
    ; Sampling interval in microseconds
    SamplingInterval={1e6 / S_FREQ:f}

    [Binary Infos]
    BinaryFormat={BV_DATATYPE}

    [Channel Infos]
    ; Each entry: Ch<Channel number>=<Name>,<Reference channel name>,
    ; <Resolution in "Unit">,<Unit>, Future extensions..
    ; Fields are delimited by commas, some fields might be omitted (empty).
    """
    # found a way to write \1
    vhdr_txt += r'; Commas in channel names are coded as "\1".'
    vhdr_txt += '\n'

    output = []
    for i, chan in enumerate(chans):
        output.append(f'Ch{i + 1:d}={chan},,{RESOLUTION},µV')

    with filename.open('w') as f:
        f.write(dedent(vhdr_txt) + '\n'.join(output))


def _write_vmrk(filename):

    vmrk_txt = f"""\
    Brain Vision Data Exchange Marker File, Version 1.0

    [Common Infos]
    Codepage=UTF-8
    DataFile={filename.name}

    [Marker Infos]
    ; Each entry: Mk<Marker number>=<Type>,<Description>,<Position in data points>,
    ; <Size in data points>, <Channel number (0 = marker is related to all channels)>
    ; Fields are delimited by commas, some fields might be omitted (empty).
    """
    vmrk_txt = dedent(vmrk_txt)
    # found a way to write \1
    vmrk_txt += r'; Commas in type or description are coded as "\1".'
    vmrk_txt += f'\nMk1=New Segment,,1,1,0,{fake_time:%Y%m%d%H%M%S%f}\n'

    with filename.open('w') as f:
        f.write(vmrk_txt)
