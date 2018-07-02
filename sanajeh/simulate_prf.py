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
from numpy.random import seed, random
from bidso.utils import replace_underscore
import numpy as np
import popeye.utilities as utils

from popeye.visual_stimulus import VisualStimulus, simulate_bar_stimulus
from popeye.og import GaussianModel
from popeye import og

from .ieeg import fake_time


S_FREQ = 500
N_CHAN = 10
DUR = 1
STIM_FILE = 'prf.npy'

SCREEN_WIDTH = 25
N_PIXELS = 100
VIEWING_DISTANCE = SCREEN_WIDTH / (tan(pi / 360 * N_PIXELS) * 2)


def simulate_prf(bids_dir, task_prf):
    prf_file = task_prf.get_filename(bids_dir)

    bars = generate_bars()
    stimulus = generate_stimulus(bars)
    model = generate_model(stimulus)
    dat = generate_population_data(model)

    chan = _make_chan_name(n_chan=N_CHAN)
    data = Data(data=dat, s_freq=S_FREQ, chan=chan, time=arange(dat[0].shape[0]) / S_FREQ)
    print((abs(data.data[0]).flatten()).sum())

    data.start_time = fake_time
    data.export(prf_file, 'bids')

    create_prf_events(replace_underscore(prf_file, 'events.tsv'), bars.shape[2])

    stimuli_dir = bids_dir / 'stimuli'
    stimuli_dir.mkdir(exist_ok=True, parents=True)
    bar_file = stimuli_dir / STIM_FILE
    save(bar_file, bars)
    assert False


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


def generate_model(stimulus):
    model = GaussianModel(stimulus, nohrf)
    model.hrf_delay = 0
    model.mask_size = 6
    return model


def generate_population_data(model):
    seed(1)
    # generate a random pRF estimate
    x = 10
    y = 10
    sigma = 2
    beta = 1
    BASELINE = 0

    FREQ = 70
    t = arange(S_FREQ * DUR) / S_FREQ

    self = model
    # mask for speed
    mask = self.distance_mask(x, y, sigma)
    print(mask.max())

    # generate the RF
    rf = og.generate_og_receptive_field(x, y, sigma, self.stimulus.deg_x, self.stimulus.deg_y)
    rf /= (2 * np.pi * sigma**2) * 1/np.diff(self.stimulus.deg_x[0,0:2])**2
    print(rf.max())

    # extract the stimulus time-series
    response = og.generate_rf_timeseries(self.stimulus.stim_arr, rf, mask)
    print(response.max())

    # convolve it with the stimulus
    idat = og.fftconvolve(response, self.hrf())[0:len(response)]
    print(idat.max())

    # units
    idat = utils.percent_change(idat)
    print(idat.max())


    dat = []
    for i in range(N_CHAN):
        i_dat = model.generate_prediction(x, y, sigma, beta, BASELINE, unscaled=True)
        print(i_dat[:10])
        i_dat -= i_dat.min()

        x = i_dat[:, None] * sin(2 * pi * t * FREQ)
        dat.append(x.flatten())

    return array(dat)


def create_prf_events(tsv_file, n_events):

    with tsv_file.open('w') as f:
        f.write('onset\tduration\ttrial_type\tstim_file\tstim_file_index\n')
        for i in range(n_events):
            f.write(f'{i * DUR}\t{DUR:f}\t{i + 1:d}\t{STIM_FILE}\t{i + 1:d}\n')
