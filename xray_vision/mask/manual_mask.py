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
"""This module will allow to draw a manual mask or region of interests(roi's)
for an image"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import logging

import numpy as np
from scipy import ndimage
from matplotlib.widgets import Lasso
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib import path
from ..utils.mpl_helpers import ensure_ax_meth

logger = logging.getLogger(__name__)


class ManualMask(object):
    @ensure_ax_meth
    def __init__(self, ax, image, cmap='gray'):
        """
        Use a GUI to specify region(s) of interest.

        The user can draw as many regions as desired and, at any point
        during the process, access the results programatically using
        the attributes below.

        Note the following keyboard shortcuts:
        r - remove (cut holes)
        a - add (resume normal drawing)
        u - undo

        Parameters
        ----------
        ax : Axes, optional
        image : array
            backdrop shown under drawing
            This is used for visual purposes and to set the shape of the
            drawing canvas. Its content does not affect the output.
        cmap : str, optional
            'gray' by default

        Attributes
        ----------
        mask : boolean array
            all "postive" regions are True, negative False
        label_array : integer array
            each contiguous region is labeled with an integer
        label_by_stroke : integer array
            Each region drawn by the user is labeled with an integer.
            Even regions that are contiguous or overlapping are given
            unique labels if they were drawn separately. Where regions
            overlap, the last-drawn region takes precedence.
        sign : boolean
            While True, all drawings add to the region(s) of interest.
            While False, all drawing cuts holes in any regions of interest.

        Methods
        -------
        undo()
            Undo the last-drawn region.

        Example
        -------
        >>> m = ManualMask(my_img)
        >>> boolean_array = m.mask  # inside ROI(s) is True, outside False
        >>> label_array = m.label_array  # a unique number for each ROI
        """
        mask_cmap = ListedColormap([(1, 1, 1, 0), 'b'])
        norm = BoundaryNorm([0, 0.5, 1], mask_cmap.N, clip=True)

        self._cid = None

        self.ax = ax
        self._base_format_fuc = ax.format_coord

        def wrapped_format_coord(x, y):
            return "{} {}".format(self._active, self._base_format_fuc(x, y))

        self.ax.format_coord = wrapped_format_coord

        self.canvas = ax.figure.canvas
        self.img_shape = image.shape
        self.data = image
        self.mask = np.zeros(self.img_shape, dtype=bool)

        self.base_image = ax.imshow(self.data, zorder=1, cmap=cmap,
                                    interpolation='nearest')
        self.overlay_image = ax.imshow(self.mask,
                                       zorder=2,
                                       alpha=.66,
                                       cmap=mask_cmap,
                                       norm=norm,
                                       interpolation='nearest')
        ax.set_title("'i': lasso, 't': pixel flip, shift inverts lasso, "
                     "'r': reset mask, 'q': no tools")

        y, x = np.mgrid[:image.shape[0], :image.shape[1]]
        self.points = np.transpose((x.ravel(), y.ravel()))
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self._active = ''
        self.lasso = None
        self._remove = False

    def _lasso_on_press(self, event):
        if self.canvas.widgetlock.locked():
            if self.canvas.widgetlock.isowner(self.lasso):
                self.canvas.widgetlock.release(self.lasso)
            else:
                return
        if event.inaxes is not self.ax:
            return
        self._remove = event.key == 'shift'
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata),
                           self._lasso_call_back)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)

    def _lasso_call_back(self, verts):
        self.canvas.widgetlock.release(self.lasso)
        p = path.Path(verts)

        new_mask = p.contains_points(self.points).reshape(*self.img_shape)
        if self._remove:
            self.mask = self.mask & ~new_mask
        else:
            self.mask = self.mask | new_mask

        self.overlay_image.set_data(self.mask)

        self.canvas.draw_idle()
        self.lasso = None

    def _pixel_flip_on_press(self, event):
        if event.inaxes is not self.ax:
            return
        x, y = int(event.xdata + .5), int(event.ydata + .5)
        if 0 <= x < self.img_shape[1] and 0 <= y <= self.img_shape[0]:
            self.mask[y, x] = ~self.mask[y, x]

        self.overlay_image.set_data(self.mask)

        self.canvas.draw_idle()

    # TODO
    def reset(self):
        self.mask *= False
        self.overlay_image.set_data(self.mask)
        self.canvas.draw_idle()
        pass

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes:
            return
        if event.key == 'i':
            self.enable_lasso()
        elif event.key == 't':
            self.enable_pixel_flip()
        elif event.key == 'r':
            self.reset()
        elif event.key == 'q':
            self.disable_tools()

    def enable_lasso(self):
        # turn off anything else
        self.disable_tools()

        self._cid = self.canvas.mpl_connect('button_press_event',
                                            self._lasso_on_press)
        self._active = 'lasso'

    def enable_pixel_flip(self):
        # turn off anything else
        self.disable_tools()

        self._cid = self.canvas.mpl_connect('button_press_event',
                                            self._pixel_flip_on_press)
        self._active = 'pixel flip'

    def disable_tools(self):
        if self._cid is not None:
            self.canvas.mpl_disconnect(self._cid)
            self._cid = None
            if self.lasso and self.canvas.widgetlock.isowner(self.lasso):
                self.canvas.widgetlock.release(self.lasso)
                self.lasso = None

        self._active = ''
        self.canvas.toolbar.set_message('')

    @property
    def label_array(self):
        arr, num = ndimage.measurements.label(self.mask)
        return arr
