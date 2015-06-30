# ######################################################################
# Copyright (c) 2015, Brookhaven Science Associates, Brookhaven        #
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
import numpy as np
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


class CDIPlotter(object):
    """
    This class plots results from CDI reconstruction.
    """

    @classmethod
    def from_axes(cls, ax0, ax1, ax2, ax3):
        """
        Set the axes from outside. The axes will be cleared
        once they are passed in. This means users can not use
        this function to overlay multiple calls

        Parameters
        ----------
        ax0 : matplotlib.axes.Axes
        ax1 : matplotlib.axes.Axes
        ax2 : matplotlib.axes.Axes
        ax3 : matplotlib.axes.Axes
        """
        plot = CDIPlotter()
        # clear the axes
        ax0.cla()
        ax1.cla()
        ax2.cla()
        ax3.cla()
        plot.ax0 = ax0
        plot.ax1 = ax1
        plot.ax2 = ax2
        plot.ax3 = ax3

        plot.figures = set([ax0.figure, ax1.figure, ax2.figure, ax3.figure])

        return plot

    @classmethod
    def create_figure(cls, figsize=None):
        """
        Initialization of a figure.

        Parameters
        ----------
        figsize : tuple
            size of the figure
        """
        if figsize is None:
            figsize = (10, 8)

        plot = CDIPlotter()
        plot.fig = plt.figure(figsize=figsize)
        plot.ax0 = plot.fig.add_subplot(2, 2, 1)
        plot.ax0.set_title('Reconstructed amplitude')
        plot.im0 = None

        plot.ax1 = plot.fig.add_subplot(2, 2, 2, sharex=plot.ax0, sharey=plot.ax0)
        plot.ax1.set_title('Reconstructed phase')
        plot.im1 = None

        plot.ax2 = plot.fig.add_subplot(2, 2, 3)
        plot.ax2.set_ylim([0, 1.2])

        plot.line1 = None
        plot.line2 = None

        plot.ax3 = plot.fig.add_subplot(2, 2, 4)
        plot.ax3.set_title('Total sample erea')
        plot.line3 = None
        plot.figures = [plot.fig]
        return plot

    def plot(self, sample_obj, obj_error, diff_error, sup_error):
        """
        Update plotting results.

        Parameters
        ----------
        sample_obj : array
            2D array of complex number
        obj_error : array
            the relative error of sample object
        diff_error : array
            calculated as the difference between new diffraction
            pattern and the original diffraction pattern
        sup_error : array
            stores the size of the sample support.
        """
        try:
            self.im0.set_data(np.abs(sample_obj))
            self.im0.set_data(np.abs(sample_obj))
            self.im1.set_data(np.angle(sample_obj))
            self.line1.set_ydata(obj_error)
            self.line2.set_ydata(diff_error)
            self.line3.set_ydata(sup_error)
        except AttributeError:
            # will only be raised the first time
            self.im0 = self.ax0.imshow(np.abs(sample_obj))
            self.im1 = self.ax1.imshow(np.angle(sample_obj))
            self.line1, = self.ax2.plot(obj_error, 'r-', label='Object error')
            self.line2, = self.ax2.plot(diff_error, 'g-', label='Diffraction error')
            self.ax3.set_ylim([0, np.size(sample_obj)])
            self.line3, = self.ax3.plot(sup_error)
            self.ax2.legend()
            self.ax3.set_ylim([0, np.size(sample_obj)])
            self.line3, = self.ax3.plot(sup_error)
        finally:
            for fig in self.figures:
                fig.canvas.draw()
