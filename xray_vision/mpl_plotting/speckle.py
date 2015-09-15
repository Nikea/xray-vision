# ######################################################################
# Copyright (c) 2014, Brookhaven Science Associates, Brookhaven        #
# National Laboratory. All rights reserved.                            #
#                                                                      #
# Developed at the NSLS-II, Brookhaven National Laboratory             #
# Developed by Sameera K. Abeykoon, April 2014                         #
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
import matplotlib.ticker as mticks
from .utils import multiline
import logging
logger = logging.getLogger(__name__)

"""
    Plotting tools for X-Ray Speckle Visibility Spectroscopy(XSVS)
    Analysis tools can be found at scikit-xray.speckle_analysis module
"""


def mean_intensity_plotter(ax, mean_intensity_sets, index_list,
                           title="Mean intensities",
                           xlabel="Frames", ylabel="Mean Intensity"):
    """
    This will plot mean intensities for ROIS' of the labeled array
    for different image sets.

    Parameters
    ----------
    ax : list of Axes
        list of `Axes` objects to add the artist tool
    mean_intensity_sets : list
        Average intensities of each ROI as a list
        shape len(images_sets)
    index_list : list
        labels list for each image set
    title : str, optional
        title of the plot
    x_label : str, optional
        x axis label
    y_label : str, optional
        y axis label
    
    Returns
    -------
    artists : list of lists
        List of lists of the line artists

    """
    artists = []
    if np.all(map(lambda x: x == index_list[0], index_list)) is False:
        raise ValueError("Labels list for the image sets are different")
    
    ax[len(index_list[0])-1].set_xlabel(xlabel)
    for i in range(len(index_list[0])):
        ax[i].set_ylabel(ylabel)
        ax[i].set_title(title+" for ROI " + str(i+1))
        total = 0
        first = 0
        x = [len(elm) for elm in mean_intensity_sets]
        x_val = np.arange(sum(x))
        arts = []
        for j in range(len(mean_intensity_sets)):
            total += x[j]
            art, = ax[i].plot(x_val[first:total], 
                              mean_intensity_sets[j][:, i],
                              label=str(j+1)+" image_set")
            arts.append(art)
            first = total
        artists.append(arts)
        ax[i].legend().draggable()
    return arts


def combine_intensity_plotter(ax, combine_intensity,
                              title="Mean Intensities - All Image Sets",
                              xlabel="Frames", ylabel="Mean Intensity",
                              label=" ROI"):
    """
    This will plot the combine intensities for all image sets

    Parameters
    ----------
    ax : Axes
        The `Axes` object to add the artist tool

    combine_intensity : array
        combine intensities for each ROI from image data sets

    title : str, optional
        title of the plot

    x_label : str, optional
        x axis label

    y_label : str, optional
        y axis label
    """
    num_rois = combine_intensity.shape[1]
    for i in range(num_rois):
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.set_title(title)
        ax.plot(combine_intensity[:, i], label=str(i+1)+label)
    ax.legend()


def circular_average_plotter(ax, image_data, ring_averages, bin_centers,
                             im_title="Image Data", 
                             line_title="Circular Average",
                             line_xlabel="Bin Centers",
                             line_ylabel="Ring Average", 
                             im_kw=None, line_kw=None):
    """This will plot image data and circular average of the that image data
    
    Specific plot that was asked for by 11id at NSLS2.
    
    Parameters
    ----------
    ax : tuple
        Two axes. First is for displaying the image with imshow. Second is 
        for plotting the circular average with semilogy
    image_data : array
    ring_averages : array
    bin_centers: array
    im_title : str, optional
        title for the image data
    line_title : str, optional
        title for the circular avergae of image data
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

    line, = ax[1].semilogy(bin_centers, ring_averages, **line_kw)
    ax[1].set_title(line_title)
    ax[1].set_xlabel(line_xlabel)
    ax[1].set_ylabel(line_ylabel)
    
    return (im, line)

def kymograph(ax, data, title="Kymograph", xlabel="Pixel", 
              ylabel="Frame", fps=None, frame_offset=0, **im_kw):
    """Plot the array of pixels (x, col) versus frame (y, row[kymograph_datay])

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
                  ylabel='Intensity', label="ROI "):
    """Plot each entry in 'data' in its own matplotlib line plot

    Parameters
    ----------
    ax : list of Axes
        The matplotlib.axes.Axes objects in which to plot `data`
    data : list
        List of intensities. Each entry in the list should be a 1-D numpy array
    title : str, optional
        Will be added above the top axes
    x_label : str, optional
        x axis label. Will be added to the bottom axes
    y_label : str, optional
        y axis label. Will be added to all axes
    label : str, optional
        Prefix for the legend. Will be formatted as 'label #' where # is the index of 
        the data list plus 1
    
    Returns
    -------
    arts : list
        List of matplotlib.lines.Line2D objects that can be used for further manipulation 
        of the plots
    """
    num_rois = len(data)
    # set the title on the first axes
    ax[0].set_title(title)
    labels = [label + str(i+1) for i in range(len(data))]
    # set the ylabels on all the axes
    ylabels = [ylabel] * len(data)
    arts = multiline(ax, data, labels, ylabels=ylabels)
    # set the x axis on the last axes
    ax[-1].set_xlabel(xlabel)
    return arts
