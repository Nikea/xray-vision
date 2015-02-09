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

from atom.api import (Atom, Typed, Str, Dict, observe, Float)
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from bubblegum.backend.mpl.stack_1d import Stack1DView


class Plot1dModel(Atom):
    _fig = Typed(Figure)
    _ax = Typed(Axes)
    _data_stack = Typed(Stack1DView)
    _data_dict = Dict()
    _cmap = Str()
    _norm = Str()
    horz_offset = Float()
    vert_offset = Float()

    def __init__(self):
        with self.suppress_notifications():
            # plotting initialization
            self._fig = Figure(figsize=(1,1))
            self._fig.set_tight_layout(True)
            self._data_dict = {}
            self._ax = self._fig.add_subplot(111)

        self._data_stack = Stack1DView(ax=self._ax,
                                       data_dict=self._data_dict)
    @observe('horz_offset')
    def update_horz_offset(self, changed):
        print('horz_offset changed')
        self._data_stack.set_horz_offset(self.horz_offset)
        self.replot()

    @observe('vert_offset')
    def update_vert_offset(self, changed):
        print('vert_offset changed')
        self._data_stack.set_vert_offset(self.vert_offset)
        self.replot()

    @observe('_data_dict')
    def update_data(self, changed):
        print('data_dict update triggered')
        if self._data_stack.data_dict is not self._data_dict:
            self._data_stack.data_dict = self._data_dict
        self.replot()

    def update_data(self, name, x, y):
        self._data_dict[name] = (x, y)
        self.replot()

    @property
    def axes(self):
        return self._ax

    @property
    def figure(self):
        return self._fig

    def replot(self):
         self._data_stack.replot()
