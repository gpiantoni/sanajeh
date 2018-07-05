from ctypes import c_int16
from wonambi import Data
from wonambi.utils.simulate import _make_chan_name
from numpy import (append,
                   arange,
                   array,
                   insert,
                   pi,
                   save,
                   sin,
                   tan,
                   )
from bidso.utils import replace_underscore

from popeye.visual_stimulus import VisualStimulus, simulate_bar_stimulus
from popeye.og import GaussianModel
from popeye.utilities import spm_hrf

from .ieeg import fake_time
from .fmri import create_bold, TR


S_FREQ = 500
N_CHAN = 10
DUR = 1
STIM_FILE = 'prf.npy'

SCREEN_WIDTH = 25
N_PIXELS = 100
VIEWING_DISTANCE = SCREEN_WIDTH / (tan(pi / 360 * N_PIXELS) * 2)


def simulate_bold_prf(bids_dir, task_prf):
    prf_file = task_prf.get_filename(bids_dir)
    prf_file.parent.mkdir(exist_ok=True, parents=True)
    bars = generate_bars()
    stimulus = generate_stimulus(bars)
    model = generate_model(stimulus, spm_hrf)
    X = -2
    Y = 2
    SIGMA = 2
    BETA = 1
    BASELINE = 0
    dat = model.generate_prediction(X, Y, SIGMA, BETA, BASELINE)

    create_bold(prf_file, task_prf.task, 11143, dat)

    tsv_file = replace_underscore(prf_file, 'events.tsv')
    create_prf_events(tsv_file, bars.shape[2], TR)


def simulate_ieeg_prf(bids_dir, task_prf):
    prf_file = task_prf.get_filename(bids_dir)

    bars = generate_bars()
    stimulus = generate_stimulus(bars)
    model = generate_model(stimulus, nohrf)
    dat = generate_population_data(model, N_CHAN)

    chan = _make_chan_name(n_chan=N_CHAN)
    data = Data(data=dat, s_freq=S_FREQ, chan=chan, time=arange(dat[0].shape[0]) / S_FREQ)

    data.start_time = fake_time
    data.export(prf_file, 'bids')

    tsv_file = replace_underscore(prf_file, 'events.tsv')
    create_prf_events(tsv_file, bars.shape[2], DUR)

    stimuli_dir = bids_dir / 'stimuli'
    stimuli_dir.mkdir(exist_ok=True, parents=True)
    bar_file = stimuli_dir / STIM_FILE
    save(bar_file, bars)


def generate_bars():
    thetas = arange(0, 360, 90)
    thetas = insert(thetas, 0, -1)
    thetas = append(thetas, -1)
    num_blank_steps = 30
    num_bar_steps = 30
    ecc = 12
    bar = simulate_bar_stimulus(N_PIXELS, N_PIXELS, VIEWING_DISTANCE,
                                SCREEN_WIDTH, thetas, num_bar_steps, num_blank_steps, ecc)
    return bar


def generate_stimulus(bars):
    tr_length = 1.0
    scale_factor = 1.0
    dtype = c_int16
    stimulus = VisualStimulus(bars, VIEWING_DISTANCE, SCREEN_WIDTH, scale_factor, tr_length, dtype)

    return stimulus


def nohrf(*args):
    return array([1, ])


def generate_model(stimulus, hrf_func):
    model = GaussianModel(stimulus, hrf_func)
    model.hrf_delay = 0
    model.mask_size = 6
    return model


def generate_population_data(model, n_chan):
    # generate a random pRF estimate
    X = 10
    Y = 10
    SIGMA = 2
    BETA = 1
    BASELINE = 0

    FREQ = 70
    t = arange(S_FREQ * DUR) / S_FREQ

    dat = []
    for i in range(n_chan):
        i_dat = model.generate_prediction(X, Y, SIGMA, BETA, BASELINE)
        i_dat -= i_dat.min()

        x = i_dat[:, None] * sin(2 * pi * t * FREQ)
        dat.append(x.flatten())

    return array(dat)


def create_prf_events(tsv_file, n_events, dur):

    with tsv_file.open('w') as f:
        f.write('onset\tduration\ttrial_type\tstim_file\tstim_file_index\n')
        for i in range(n_events):
            f.write(f'{i * dur}\t{dur:f}\t{i + 1:d}\t{STIM_FILE}\t{i + 1:d}\n')
