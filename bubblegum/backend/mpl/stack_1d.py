# ######################################################################
# Copyright (c) 2014, Brookhaven Science Associates, Brookhaven        #
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
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from matplotlib import cm
import numpy as np

from . import AbstractMPLDataView

import logging
logger = logging.getLogger(__name__)


class Stack1DView(AbstractMPLDataView):
    """
    The OneDimStackViewer provides a UI widget for viewing a number of 1-D
    data sets with cumulative offsets in the x- and y- directions.  The
    first data set always has an offset of (0, 0).

    Attributes
    ----------
    data_source : bubblegum.data.DataSource
    """

    _default_horz_offset = 0
    _default_vert_offset = 0
    _default_autoscale = False

    def __init__(self, fig, data_dict, cmap=None, norm=None):
        """
        __init__ docstring

        Parameters
        ----------
        fig : figure to draw the artists on
        data_source : dict
            Dictionary formatted like: {data_name: (x, y)}
        cmap : colormap that matplotlib understands
        norm : mpl.colors.Normalize
        """
        self._data_dict = data_dict
        # call the parent constructors
        super(Stack1DView, self).__init__(fig=fig, cmap=cmap, norm=norm)

        # set some defaults
        self._horz_offset = self._default_horz_offset
        self._vert_offset = self._default_vert_offset
        self._autoscale = self._default_autoscale

        # create the matplotlib axes
        self._ax = self._fig.add_subplot(1, 1, 1)
        self._ax.set_aspect('equal')
        # create an ordered dict of lines that has identical keys as the
        # data_dict
        self._lines = {}

        # create a local counter
        # add the data to the main axes
        for idx, (key, (x, y)) in enumerate(six.iteritems(self._data_dict)):
            # plot the (x,y) data with default offsets
            self._lines[key] = self._ax.plot(
                x + idx * self._horz_offset,
                y + idx * self._vert_offset)[0]

    def set_vert_offset(self, vert_offset):
        """
        Set the vertical offset for additional lines that are to be plotted

        Parameters
        ----------
        vert_offset : number
            The amount of vertical shift to add to each line in the data stack
        """
        self._vert_offset = vert_offset
        self.replot()

    def set_horz_offset(self, horz_offset):
        """
        Set the horizontal offset for additional lines that are to be plotted

        Parameters
        ----------
        horz_offset : number
            The amount of horizontal shift to add to each line in the data
            stack
        """
        self._horz_offset = horz_offset
        self.replot()

    def replot(self):
        """
        @Override
        Replot the data after modifying a display parameter (e.g.,
        offset or autoscaling) or adding new data
        """
        rgba = cm.ScalarMappable(self._norm, self._cmap)
        # determine the number of data sets in the data_dict to compute the
        # color for the line
        num_datasets = len(self._data_dict)

        for idx, (key, (x, y)) in enumerate(six.iteritems(self._data_dict)):
            # compute the new horizontal and vertical offsets
            new_x = x+idx * self._horz_offset
            new_y = y+idx * self._vert_offset

            # compute the color for the line
            color = rgba.to_rgba(x=(idx / num_datasets))
            try:
                # set the data in the corresponding line
                self._lines[key].set_xdata(x + idx * self._horz_offset)
                self._lines[key].set_ydata(y + idx * self._vert_offset)
                # set the color
                self._lines[key].set_color(color)
            except KeyError:
                # create a new line if the key does not exist
                self._lines[key] = self._ax.plot(new_x, new_y, color=color)[0]

        # check to see if the axes need to be automatically adjusted to show
        # all the data
        if self._autoscale:
            self._ax.relim(visible_only=True)
            self._ax.autoscale_view(tight=True)
        self._fig.canvas.draw()

    def set_auto_scale(self, is_autoscaling):
        """
        Enable/disable autoscaling of the axes to show all data

        Parameters
        ----------
        is_autoscaling: bool
            Automatically rescale the axes to show all the data (true)
            or stop automatically rescaling the axes (false)
        """
        self._autoscale = is_autoscaling
        self.replot()

    def find_range(self):
        """
        Find the min/max in x and y

        @tacaswell: I'm sure that this is functionality that matplotlib
            provides but i'm not at all sure how to do it...

        Returns
        -------
        (min_x, max_x, min_y, max_y)
        """
        if len(self._ax.lines) == 0:
            return 0, 1, 0, 1

        # find min/max in x and y
        min_x = np.zeros(len(self._ax.lines))
        max_x = np.zeros(len(self._ax.lines))
        min_y = np.zeros(len(self._ax.lines))
        max_y = np.zeros(len(self._ax.lines))

        for idx in range(len(self._ax.lines)):
            min_x[idx] = np.min(self._ax.lines[idx].get_xdata())
            max_x[idx] = np.max(self._ax.lines[idx].get_xdata())
            min_y[idx] = np.min(self._ax.lines[idx].get_ydata())
            max_y[idx] = np.max(self._ax.lines[idx].get_ydata())

        return np.min(min_x), np.max(max_x), np.min(min_y), np.max(max_y)

    def clear_data(self):
        """
        @Override
        Override abstract base class to also clear the ordered dict mpl lines
        """
        # clear all lines from the lines_dict
        self._lines.clear()
        # clear the artists
        self._ax.cla()
        # remove the data source
        self._data_dict = None
        # call the replot function
        self.replot()
