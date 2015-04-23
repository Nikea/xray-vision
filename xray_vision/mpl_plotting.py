from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import numpy as np
import matplotlib.cm as mcm
import copy


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
    im = ax.imshow(label_array, cmap=cmap,
                   interpolation='nearest',
                   vmin=vmin,
                   **kwargs)

    return im
