import matplotlib
matplotlib.use('Agg')
from xray_vision.mpl_plotting import speckle
from nose.tools import raises
import matplotlib.pyplot as plt
import numpy as np

def test_roi_plotter():
    fig, ax = plt.subplots(nrows=2)
    data = [np.random.random((100)), np.random.random((200))]
    speckle.rois_as_lines(ax, data)

def test_kymograph_plotter():
    """Make sure that the tick formatter is floats/ints depending on input data
    
    This also serves as a smoke test for the kymograph plotter
    """
    fig, ax = plt.subplots()
    data = np.random.random((50, 50))
    im, cb = speckle.kymograph(ax, data)
    assert cb.locator._integer is False
    
    fps = 10
    frame_offset = 10
    data = np.random.randint(0, 1000, size=(50,60))
    im, cb = speckle.kymograph(ax, data, fps=fps, frame_offset=frame_offset)
    assert cb.locator._integer is True
    
    # verify the extent
    extent = im._extent
    assert extent[0] == 0
    assert extent[1] == data.shape[1]
    assert extent[2] == frame_offset / fps
    assert extent[3] == (frame_offset + data.shape[0]) / fps
