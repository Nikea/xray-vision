import matplotlib
matplotlib.use('Agg')
from xray_vision.mpl_plotting import utils
from nose.tools import raises
import matplotlib.pyplot as plt
import numpy as np


@raises(ValueError)
def _multiline_fail(ax, data, labels, line_kw=None, xlabels=None, 
                    ylabels=None):
    utils.multiline(ax, data, labels, line_kw, xlabels, ylabels)


def _multiline_pass(ax, data, labels, line_kw=None, xlabels=None, 
                    ylabels=None):
    utils.multiline(ax, data, labels, line_kw, xlabels, ylabels)

def test_multiline():
    fig, ax = plt.subplots()
    
    fails = [
        {'data': np.random.random((50, 3)), 'labels': '50x3'},
        {'data': np.random.random((3, 50)), 'labels': '3x50'},
        {'data': np.random.random((4, 4, 4)), 'labels': '4x4x4'},
    ]
    
    for f in fails:
        yield _multiline_fail, [ax], [f['data']], [f['labels']]
