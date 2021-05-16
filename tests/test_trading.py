from Artha.trading import *
from .test_data.trading_data import *
import pytest
import numpy as np

@pytest.mark.parametrize("data,spike_indexes,window", volume_data)
def test_vol_spikes(data, spike_indexes, window):
    assert vol_spikes(data, window) == spike_indexes