from __future__ import absolute_import, division, print_function

import six
import numpy as np
import copy
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.ticker import NullLocator


def mark_region(ax, low, high, vline_style, span_style):
    """
    Mark a region of a graph with vertical lines and an axvspan

    Parameters
    ----------
    ax : Axes
        The `Axes` object to add the artist too

    low, high : float
        The low and high threshold values, points for `low < x < high` are
        styled using `inner_style` and points for `x < low or x > high` are
        styled using `outer_style`

    vline_style : dict, optional
        The style to use for the vertical lines

    span_stlye : dict, optional
        Style for axvspan behind central region

    Returns
    -------

    vline_low, vline_hi : Line2D
        Vertical lines at the thresholds

    hspan : Patch
        Patch over middle region

    """

    # add vertical lines
    vline_low = ax.axvline(low, **vline_style)
    vline_high = ax.axvline(high,  **vline_style)

    hspan = ax.axvspan(low, high, **span_style)

    return vline_low, vline_high, hspan


def split_plot(ax, x, y, low, high, inner_style, outer_style):
    """
    Split styling of line based on the x-value

    Parameters
    ----------
    ax : Axes
        The `Axes` object to add the artist too

    x, y : ndarray
        Data, must be same length

    low, high : float
        The low and high threshold values, points for `low < x < high` are
        styled using `inner_style` and points for `x < low or x > high` are
        styled using `outer_style`

    inner_style, outer_style : dict
        Dictionary of styles that can be passed to `ax.plot`

    Returns
    -------
    lower, mid, upper : Line2D
        The artists for the lower, midddle, and upper ranges
    """

    low_mask = x < low
    high_mask = x > high
    mid_mask = ~np.logical_or(low_mask, high_mask)

    low_mask[1:] |= low_mask[:-1]
    high_mask[:-1] |= high_mask[1:]

    lower, = ax.plot(x[low_mask], y[low_mask], **outer_style)
    mid, = ax.plot(x[mid_mask], y[mid_mask], **inner_style)
    upper, = ax.plot(x[high_mask], y[high_mask], **outer_style)

    return lower, mid, upper


def show_label_array(ax, label_array, cmap=None, **kwargs):
    """
    Display a labeled array nicely

    Additional kwargs are passed through to `ax.imshow`.
    If `vmin` is in kwargs, it is clipped to minimum of 0.5.

    Parameters
    ----------
    ax : Axes
        The `Axes` object to add the artist too

    label_array : ndarray
        Expected to be an unsigned integer array.  0 is background,
        positive integers label region of interent

    cmap : str or colormap, optional
        Color map to use, defaults to 'Paired'


    Returns
    -------
    img : AxesImage
        The artist added to the axes
    """
    if cmap is None:
        cmap = 'Paired'

    _cmap = copy.copy((mcm.get_cmap(cmap)))
    _cmap.set_under('w', 0)
    vmin = max(.5, kwargs.pop('vmin', .5))

    ax.set_aspect('equal')
    im = ax.imshow(label_array, cmap=_cmap,
                   interpolation='nearest',
                   vmin=vmin,
                   **kwargs)

    return im


def binary_state_lines(ax, data, xmin, xmax,
                       delta_y=3,
                       off_color=None,
                       on_color=None,
                       lc_kwargs=None):
    """
    Draw series of lines indicating the state of (many) indicators.

    Parameters
    ----------
    ax : Axes
        The axes to draw stuff to

    data : OrderedDict
        The data as an ordered dict. The keys will be used as ytick labels
        keyed on the data label.  The values are a list of edge pairs where
        the value is 'high'; ex ``data[k] = [(1, 2), (3, 5.5)]`` is 'high' in
        the ranges 1 to 2 and 3 to 5.5 and 'low' everywhere else.

        The lines are drawn in order from the top down.

    xmin, xmax : float
        The minimum and maximum limits for the x values

    delta_y : float, optional
        The spacing between lines

    off_color, on_color : color, optional
        The colors to use for the the off/on state.
        Default to "#1C2F4D" (blueish) and "#FA9B00" (yellowish) respectively

    lc_kwargs : dict, optional
       kwargs to pass through the the LineCollection init method.  If not
       given defaults to ``{'lw': 10}``

    Returns
    -------
    ret : dict
        dictionary of the collections added keyed on the label

    """
    if lc_kwargs is None:
        lc_kwargs = dict()
    if 'lw' not in lc_kwargs:
        lc_kwargs['lw'] = 10

    if off_color is None:
        off_color = "#1C2F4D"
    if on_color is None:
        on_color = "#FA9B00"

    # base offset
    y_val = 0
    # make the color map and norm
    cmap = ListedColormap([off_color, on_color])
    norm = BoundaryNorm([0, 0.5, 1], cmap.N)
    # dictionary to hold the returned artists
    ret = dict()
    # loop over the input data draw each collection
    for label, d in data.items():
        # increment the y offset
        y_val += delta_y
        # turn the high windows on to alternating
        # high/low regions
        x = np.asarray(d).ravel()
        # assign the high/low state to each one
        state = np.mod(1 + np.arange(len(x)), 2)
        # deal with boundary conditions to be off
        # at start/end
        if x[0] > xmin:
            x = np.r_[xmin, x]
            state = np.r_[0, state]
        if x[-1] < xmax:
            x = np.r_[x, xmax]
            state = np.r_[state, 0]
        # make the matching y values
        y = np.ones(len(x)) * y_val
        # call helper function to create the collection
        coll = _draw_segments(ax, x, y, state,
                              cmap, norm, lc_kwargs)
        ret[label] = coll

    # set up the axes limits
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0, y_val + delta_y)
    # turn off x-ticks
    ax.xaxis.set_major_locator(NullLocator())
    # make the y-ticks be labeled as per the input
    ax.yaxis.set_ticks((1 + np.arange(len(data))) * delta_y)
    ax.yaxis.set_ticklabels(list(data.keys()))
    # invert so that the first data is at the top
    ax.invert_yaxis()
    # turn off the frame and patch
    ax.set_frame_on(False)
    # return the added artists
    return ret


def _draw_segments(ax, x, y, state, cmap, norm, lc_kwargs):
    """
    helper function to turn boundary edges into the input LineCollection
    expects.

    Parameters
    ----------
    ax : Axes
       The axes to draw to

    x, y, state : array
       The x edges, the y values and the state of each region

    cmap : matplotlib.colors.Colormap
       The color map to use

    norm : matplotlib.ticker.Norm
       The norm to use with the color map

    lc_kwargs : dict
       kwargs to pass through to LineCollection
    """

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=cmap, norm=norm, **lc_kwargs)
    lc.set_array(state)

    ax.add_collection(lc)
    return lc
