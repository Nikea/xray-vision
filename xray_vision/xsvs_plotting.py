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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import logging
from collections import deque
import numpy as np

import matplotlib.pyplot as plt

"""
    Plotting tools for X-Ray Speckle Visibility Spectroscopy(XSVS)
"""


def mean_intensity_plotter(ax, mean_intensity_sets, index_list,
                           title="Mean intensities",
                           xlabel="Frames", ylabel="Mean Intensity"):
    """
    This will plot mean intensities for ROIS' of the labeled array
    for different image sets.

    Parameters
    ----------
     ax : Axes
        The `Axes` object to add the artist tool

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

    """
    if np.all(map(lambda x: x == index_list[0], index_list)):
        ax[len(index_list[0])-1].set_xlabel(xlabel)
        for i in range(len(index_list[0])):
            ax[i].set_ylabel(ylabel)
            ax[i].set_title(title+" for ROI " + str(i+1))
            total = 0
            first = 0
            x = [len(elm) for elm in mean_intensity_sets]
            x_val = np.arange(sum(x))
            for j in range(len(mean_intensity_sets)):
                total += x[j]
                ax[i].plot(x_val[first:total], mean_intensity_sets[j][:, i],
                           label=str(j+1)+" image_set")
                first = total
        plt.legend()
    else:
        raise ValueError("Labels list for the image sets are different")


def combine_intensity_plotter(ax, combine_intensity,
                              title="Mean Intensities - All Image Sets",
                              xlabel="Frames", ylabel="Mean Intensity"):
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
        ax.plot(combine_intensity[:, i], label=str(i+1)+" ROI")
    plt.legend()


def circular_average_plotter(ax1, ax2, image_data, ring_averages, bin_centers,
                             i_title="Image Data", c_title="Circular Average",
                             cmap="gray", vmin=None, vmax=None, marker='o',
                             line_color='blue', xlabel="Bin Centers",
                             ylabel="Ring Average"):
    """
    Parameters
    ----------
    ax1 : Axes
        The `Axes` object to add the artist tool

    ax2 : Axes
        The `Axes` object to add the artist tool

    image_data : array

    ring_averages : array

    bin_centers: array

    i_title : str, optional
        title for the image data

    c_title : str, optional
        title for the circular avergae of image data

    cmap : str, optional
        colormap for image data

    vmin : float, optional
        arguments specify the color limits

    vmax : float, optional
        arguments specify the color limits

    marker : str, optional
        line marker

    line_color : str, optional
        line color

    x_label : str, optional
        x axis label circular average plot

    y_label : str, optional
        y axis label circular average plot
    """
    ax1.imshow(image_data, cmap=cmap, vmin=vmin, vmax=vmax)
    ax1.set_title(i_title)

    ax2.semilogy(bin_centers, ring_averages, c=line_color, marker=marker)
    ax2.set_title(c_title)
    ax2.set_xlabel(xlabel)
    ax2.set_ylabel(ylabel)


def roi_kymograph_plotter(ax, kymograph_data, title="ROI Kymograph",
                          fig_size=(8, 10), xlabel="pixel list",
                          ylabel="Frames", cmap='gist_earth'):
    """
    This will plot graphical representation of pixels variation over time
    for required ROI.

    Parameters
    ----------
    ax : Axes
        The `Axes` object to add the artist tool

    kymograph_data : array
        data for graphical representation of pixels variation over time
        for required ROI

    title : str, optional
        title of the plot

    fig_size : tuple, optional
        figure size

    x_label : str, optional
        x axis label of the plot

    y_label : str, optional
        y axis label

    cmap : str, optional
        colormap for the data

    """
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.imshow(kymograph_data, cmap=cmap)


def roi_pixel_plotter(axes, roi_pixel_data, title='Intensities - ROI ', xlabel='pixel list',
                      ylabel='Intensity'):
    """
    ROI pixel plotter
    Parameters
    ----------
    ax :

    mean_intensity : array

    title : str, optional

    fig_size : tuple, optional

    x_label : str, optional

    y_label : str, optional

    """
    num_rois = len(roi_pixel_data.values())
    for i in range(num_rois):
        axes[i].plot(roi_pixel_data.values()[i])
        axes[i].set_xlabel(xlabel)
        axes[i].set_ylabel(ylabel)
        axes[i].set_title(title+str(i+1))

