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
import sys
import logging

logger = logging.getLogger(__name__)

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.widgets import Lasso
from matplotlib.patches import PathPatch
from matplotlib import path

import matplotlib.pyplot as plt
import numpy as np

"This module will allow to draw a manual mask for an image"

class ManualMask(object):
    def __init__(self, ax, image):
        self.axes = ax
        self.canvas = ax.figure.canvas
        self.data = image
        self.img_shape = image.shape
        self.mask = np.zeros(image.shape[0]*image.shape[1], dtype=bool)
        y, x = np.mgrid[:image.shape[0], :image.shape[1]]
        self.points = np.transpose((x.ravel(), y.ravel()))
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)


    def on_press(self, event):
        if self.canvas.widgetlock.locked():
           return
        if event.inaxes is None:
           return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata),
                           self.call_back)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)


    def call_back(self, verts):
        p = path.Path(verts)
        self.patch = PathPatch(p, facecolor='g')
        plt.gca().add_patch(self.patch)

        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)

        self.mask = self.mask | p.contains_points(self.points)


    def reset(self, event):
	    #TODO
         self.patch.remove()


    def key_press_callback(self, event):
        'whenever a key is pressed'
        #"press 'i' to start drawing a mask(s) on the canvas"
        #"press 'f' to stop drawing and create a text file containing
        #  the mask array"
        if not event.inaxes:
            return
        if event.key=='i':
            self.cid = self.canvas.mpl_connect('button_press_event',
                                               self.on_press)
        if event.key=='r':
            self.rcid = self.canvas.mpl_connect('button_press_event',
                                                self.reset)
        if event.key=='f':
            np.savetxt("mask_data.txt", self.mask.reshape(self.img_shape))
            np.save("mask.npy", self.mask.reshape(self.img_shape))
            plt.imshow(self.mask.reshape(self.img_shape))
            plt.show()


def manual_mask_demo(image):
    ax = plt.subplot(111)
    ax.imshow(image)
    plt.title("Press 'i'- start drawing a mask , Press 'f'- finish masking ")
    mc = ManualMask(ax, image)
    plt.show()


if __name__  == "__main__":
        from skimage import data
        image = data.coins()

	manual_mask_demo(image)