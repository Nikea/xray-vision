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

from matplotlib.widgets import Lasso
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib import path

import matplotlib.pyplot as plt
import numpy as np
logger = logging.getLogger(__name__)


class ManualMask(object):
    def __init__(self, ax, image):
        cmap = ListedColormap([(1, 1, 1, 0), 'b'])
        norm = BoundaryNorm([0, 0.5, 1], cmap.N, clip=True)

        self._cid = None

        self.ax = ax
        self.canvas = ax.figure.canvas
        self.img_shape = image.shape
        self.data = image
        self.mask = np.zeros(self.img_shape, dtype=bool)

        self.base_image = ax.imshow(self.data, zorder=1, cmap='gray',
                                    interpolation='nearest')
        self.overlay_image = ax.imshow(self.mask,
                                       zorder=2,
                                       alpha=.66,
                                       cmap=cmap,
                                       norm=norm,
                                       interpolation='nearest')
        ax.set_title("Press 'i'- start drawing a mask, 'q'- to finish")

        y, x = np.mgrid[:image.shape[0], :image.shape[1]]
        self.points = np.transpose((x.ravel(), y.ravel()))
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self._active = 'none'

    def _lasso_on_press(self, event):
        if self.canvas.widgetlock.locked():
            return
        if event.inaxes is None:
            return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata),
                           self._lasso_call_back)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)

    def _lasso_call_back(self, verts):
        p = path.Path(verts)

        self.canvas.widgetlock.release(self.lasso)
        new_mask = p.contains_points(self.points).reshape(*self.img_shape)
        self.mask = self.mask | new_mask

        self.overlay_image.set_data(self.mask)

        self.canvas.draw_idle()

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
        if self._cid is None and event.key == 'i':
            self.enable_lasso()
        elif event.key == 'r':
            self.reset()
        elif self._cid is not None and event.key == 'q':
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
        self._active = 'none'

if __name__ == "__main__":
    from skimage import data
    image = data.coins()
    f, ax = plt.subplots()
    mc = ManualMask(ax, image)
    plt.show()
