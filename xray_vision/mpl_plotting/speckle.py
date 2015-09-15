# ######################################################################
# Copyright (c) 2014-2015, Brookhaven Science Associates, Brookhaven   #
# National Laboratory. All rights reserved.                            #
#                                                                      #
# Redistribution and use in source and binary forms, with or without   #
# modification, are permitted provided that the following conditions   #
# are met:                                                             #
#                                                                      #
# * Redistributions of source code must retain the above copyright     #
#   notice, this list of conditions and the following disclaimer.      #
#                                                                      #
# * Redistributions in binary form must reproduce the above copyright  #
#   notice this list of conditions and the following disclaimer in     #
#   the documentation and/or other materials provided with the         #
#   distribution.                                                      #
#                                                                      #
# * Neither the name of the Brookhaven Science Associates, Brookhaven  #
#   National Laboratory nor the names of its contributors may be used  #
#   to endorse or promote products derived from this software without  #
#   specific prior written permission.                                 #
#                                                                      #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS  #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT    #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS    #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE       #
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,           #
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES   #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR   #
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)   #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,  #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OTHERWISE) ARISING   #
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   #
# POSSIBILITY OF SUCH DAMAGE.                                          #
########################################################################

from __future__ import absolute_import, division, print_function

import six
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
from .utils import multiline
import pandas as pd
import logging
logger = logging.getLogger(__name__)

"""
Plotting tools for X-Ray Speckle Visibility Spectroscopy(XSVS)
Corresponding analysis tools can be found in the `skxray.core.speckle` module
"""


def mean_intensity_plotter(ax, dataframe,
                           title="Mean intensities", xlabel="Frames",
                           ylabel="Mean Intensity", cmap=None):
    """
    This will plot mean intensities for ROIS' of the labeled array
    for different image sets.

    Parameters
    ----------
    ax : list of Axes
        List of `Axes` objects. Should have length == len(df)
    dataframe : pd.Dataframe
        The dataframe that has columns as different datasets (probably for
        different locations in the same sample) and rows as ROIs
    title : str, optional
        title of the plot
    x_label : str, optional
        x axis label
    y_label : str, optional
        y axis label
    color_cycle : str
        Matplotlib string name of colormap (see matplotlib.pyplot.colormaps()
        for a list of valid colormaps on your machine)
    
    Returns
    -------
    artists : pd.DataFrame
        Pandas DataFrame whose column/row names match the input `dataframe`
    
    Examples
    --------
    
    """
    if cmap is None:
        # TODO don't use viridis in production, yet...
        if 'viridis' in plt.colormaps():
            cmap = 'viridis'
        else:
            cmap = 'rainbow'
    cmap = plt.get_cmap(cmap)

    ax[-1].set_xlabel(xlabel)
    # capture the artists in a nested dictionary
    artists = {col_name: {} for col_name in dataframe}
    # compute the offset for each column
    offsets = []
    cur = 0
    prev = 0
    # determine how far to offset each data set
    for data in dataframe.ix[0]:
        cur = prev + len(data)
        offsets.append((prev, cur))
        prev = cur
    # loop over the rows of the dataframe
    for idx, row_label in enumerate(dataframe.index):
        # do some axes housekeeping
        ax[idx].set_ylabel(ylabel)
        ax[idx].set_title(title + ' for %s' % row_label)
        row = dataframe.ix[row_label]
        # loop over the columns of the dataframe, creating each line plot
        # one at a time
        for idx2, (column_name, color_idx) in enumerate(zip(
            dataframe, np.arange(0, 1, 1/len(row)))):
            x = range(*offsets[idx2])
            y = row.ix[column_name]
            art, = ax[idx].plot(x, y, label=column_name, color=cmap(color_idx))
            # store the artists in a nested dictionary
            artists[column_name][row_label] = art
        # enable the legend for each plot after all data has been added
        ax[idx].legend()
    return pd.DataFrame(artists)


def combine_intensity_plotter(ax, combine_intensity,
                              title="Mean Intensities - All Image Sets",
                              xlabel="Frames", ylabel="Mean Intensity",
                              labels=None):
    """
    This will plot the combine intensities for all image sets

    Parameters
    ----------
    ax : Axes
        The matplotlib.axes.Axes object to add the roi data to
    combine_intensity : list
        List of intensities for each ROI. Each element in the list should be
        a 1-D array where the x-axis is understood to be frame number
    title : str, optional
        title of the plot
    x_label : str, optional
        x axis label
    y_label : str, optional
        y axis label
    labels : list, optional
        Names for each ROI data set. If a list is provided, it should be the
        same length as the `combine_intensity` list. If a list is not provided,
        the default will be 'ROI #' where # is the index of the dataset in
        `combine_intensity`+1
    """
    num_rois = len(combine_intensity)
    if labels is None:
        labels = ['ROI ' + str(i+1) for i in range(num_rois)]
    # to utilize the multiline plotting function, we need to create a list of
    # axes that are all the same axis
    axes = [ax] * num_rois
    arts = multiline(axes, combine_intensity, labels)
    # do some housekeeping
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.legend()
    # return the artists
    return arts


def circular_average(ax, image_data, ring_averages, bin_centers,
                     im_title="Image Data", line_title="Circular Average",
                     line_xlabel="Bin Centers", line_ylabel="Ring Average",
                     im_kw=None, line_kw=None):
    """This will plot image data and circular average of the that image data
    
    Specific plot that was asked for by 11id at NSLS2.
    
    Parameters
    ----------
    ax : tuple, list, etc.
        Two axes. First is for displaying the image with imshow. Second is
        for plotting the circular average with semilogy
    image_data : array
    ring_averages : array
    bin_centers: array
    im_title : str, optional
        title for the image data
    line_title : str, optional
        title for the circular average of image data
    line_xlabel : str, optional
        x axis label for circular average plot
    line_ylabel : str, optional
        y axis label for circular average plot
    im_kw : dict, optional
        kwargs for the imshow axes
    line_kw : dict, optional
        kwargs for the semilogy axes
    
    Returns
    -------
    im : matplotlib.image.AxesImage
        The return value from imshow. Can be used for further manipulation of
        the image plot
    line : matplotlib.lines.Line2D
        The return value from semilogy. Can be used for further manipulation of
        the semilogy plot
    """
    if im_kw is None:
        im_kw = {}
    if line_kw is None:
        line_kw = {}

    im = ax[0].imshow(image_data, **im_kw)
    ax[0].set_title(im_title)
    ax[0].figure.colorbar(im, ax=ax[0])
    
    line, = ax[1].semilogy(bin_centers, ring_averages, **line_kw)
    ax[1].set_title(line_title)
    ax[1].set_xlabel(line_xlabel)
    ax[1].set_ylabel(line_ylabel)
    
    return (im, line)


def kymograph(ax, data, title="Kymograph", xlabel="Pixel",
              ylabel="Frame", fps=None, frame_offset=0, **im_kw):
    """Plot the array of pixels (x, col) versus frame (y, row[kymograph_datay])

    Note that the pixels in the resulting plot will not necessarily be square.
    This is (1) legitimate because the x- and y-axes have different units and
    (2) beneficial because it maximizes the viewable space for this image

    Parameters
    ----------
    ax : Axes
        The matplotlib `Axes` object that the kymograph data should be added to
    data : array
        data for graphical representation of pixels variation over time
    title : str, optional
        title of the plot
    x_label : str, optional
        x axis label of the plot
    y_label : str, optional
        y axis label
    cmap : str, optional
        colormap for the data
    fps : float, optional
        Convert frame number to seconds and display time on the y-axis
    frame_offset : int, optional
        This is the frame number to start counting from
    im_kw : dict
        kwargs to be passed to matplotlib's imshow function
    
    Returns
    -------
    im : matplotlib.image.AxesImage
        The return value from imshow. Can be used for further manipulation of
        the image plot
    cb : matplotlib.colorbar.colorbar
        The colorbar for the image
    """
    extent = list((0, data.shape[1], 0, data.shape[0]))
    if fps is not None:
        ylabel = 'Time (s)'
        extent[2] = frame_offset / fps
        extent[3] = extent[2] + data.shape[0] / fps
    im_kw['extent'] = extent
    im = ax.imshow(data, **im_kw)
    # do the housekeeping
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_aspect('auto')
    integer = False
    if 'int' in data.dtype.name:
        # don't use float ticks if the data is integer typed
        integer = True
    cb = ax.figure.colorbar(im, ticks=mticks.MaxNLocator(integer=integer))
    return im, cb


def rois_as_lines(ax, data, title='Intensities - ROI ', xlabel='pixels',
                  ylabel='Intensity', labels=None):
    """Plot each entry in 'data' in its own matplotlib line plot

    Parameters
    ----------
    ax : list of Axes
        The matplotlib.axes.Axes objects in which to plot `data`
    data : list
        List of intensities. Each entry in the list should be a 1-D numpy array.
        Any data that is not a 1-D numpy array will be `ravel`ed into a 1-D
        array
    title : str, optional
        Will be added above the top axes
    x_label : str, optional
        x axis label. Will be added to the bottom axes
    y_label : str, optional
        y axis label. Will be added to all axes
    labels : list, optional
        labels for the legend. Should be the same length as `data`
    
    Returns
    -------
    arts : list
        List of matplotlib.lines.Line2D objects that can be used for further manipulation
        of the plots
    """
    num_rois = len(data)
    # set the title on the first axes
    ax[0].set_title(title)
    if labels is None:
        labels = ['ROI_' + str(i+1) for i in range(len(data))]
    # set the ylabels on all the axes
    ylabels = [ylabel] * len(data)
    data = [d.ravel() for d in data]
    arts = multiline(ax, data, labels, ylabels=ylabels)
    # set the x axis on the last axes
    ax[-1].set_xlabel(xlabel)
    return arts
