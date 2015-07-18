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
    Plotting tools for X-Ray Speckle Visibility Spectroscopy
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

    num_rois : int

    mean_intensity_sets : list

    index_list : list

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
            x_val=np.arange(sum(x))
            for j in range(len(mean_intensity_sets)):
                total += x[j]
                ax[i].plot(x_val[first:total], mean_intensity_sets[j][:, i],
                         label=str(j+1)+" image_set")
                first = total
        plt.legend()
    else:
        raise ValueError("Labels list for the image sets are different")


def combine_intensity_plotter(ax, combine_intensity, title="Mean intensities",
                           xlabel="Frames", ylabel="Mean Intensity"):
    """
    This will plot the combine intensities for all image sets

    Parameters
    ----------
    ax : Axes

    num_rois : int

    mean_intensity_sets : list

    index_list : list

    title : str, optional
        title of the plot

    x_label : str, optional
        x axis label

    y_label : str, optional
        y axis label
    """
    for i in range(combin_intensity.shape[1]):
        ax.set_ylabel(ylabel)
        ax_set_xlabel(xlabel)
        ax.set_title(title)
        ax.plot(combine_intensity[:, i], label=str(j)+" ROI")
    plt.legend()


def cirular_average_plotter(ax1, ax2, image_data, ring_averages, bin_centers,
                            i_title="Image Data", c_title="Circular Average",
                            cmap="gray", vmin=None, vmax=None, marker='o',
                            line_color='blue', xlabel="Bin Centers",
                            ylabel="Ring Average", left=0.1, width = 0.65,
                            bottom= 0.1, height=0.65):
    plot_axes = [left, bottom, width, height]

    ax1.imshow(imge_data, cmap=cmap, vmin=vmin, vmax=vmax)
    ax1.set_title(i_title)

    ax2.semilogy(bin_centers, ring_averages, c=line_color, marker=maker)
    ax2.set_title(c_title)
    ax2.set_xlabel(xlabel)
    ax2.set_ylabel(ylabel)
