from __future__ import absolute_import, division, print_function
import numpy as np

def multiline(ax, data, labels, line_kw=None, xlabels=None, ylabels=None):
    """Plot a number of datasets on their own line_artist
    
    Parameters
    ----------
    ax : iterable
        List of mpl.Axes objects
    data : list
        If the data is Nx1, the data will be treated as 'x'. If the data is
        Nx2, the data will be treated as (x, y)
    labels : list
        Names of the data sets. These will appear as the legend in each plot
    line_kw : dict
        Dictionary of kwargs to be passed to **all** of the plotting functions.
    xlabels : iterable or string, optional
        The name of the x axes. If an iterable is passed in, it should be the
        same length as `data`. If a string is passed in, it is assumed that all
        'data' should have the same `x` axis
    ylabels : iterable or string, optional
        Same as `xlabels`.
    Returns
    -------
    arts : list
        Dictionary of matplotlib.lines.Line2D objects. These objects can be
        used for further manipulation of the plot
    """
    if line_kw is None:
        line_kw = {}
    arts = []
    # handle the xlabels
    if xlabels is None:
        xlabels = [''] * len(data)
    if ylabels is None:
        ylabels = [''] * len(data)
    if isinstance(xlabels, str):
        xlabels = [xlabel] * len(data)
    if isinstance(ylabels, str):
        ylabels = [ylabel] * len(data)
        
    def to_xy(d, label):
        shape = d.shape
        if len(shape) == 1:
            return range(len(d)), d
        elif len(shape) == 2:
            if shape[0] == 1:
                return range(len(d)), d[:, 1]
            elif shape[1] == 1:
                return range(len(d)), d[0]
            elif shape[0] == 2:
                return d[0], d[1]
            elif shape[1] == 2:
                return d[:, 0], d[:, 1]
                
        raise ValueError('data set "%s" has a shape I do not '
                         'understand. Expecting shape (N), (Nx1), '
                         '(1xN), (Nx2) or (2xN). I got %s' % (label, shape))
                
    for ax, d, label, xlabel, ylabel in zip(ax, data, labels, xlabels, ylabels):
        d = np.asarray(d)
        x, y = to_xy(d, label)
        
        art, = ax.plot(x, y, label=label, **line_kw)
        arts.append(art)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
    return arts
