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
from collections import defaultdict

from six.moves import zip
import numpy as np

import logging
logger = logging.getLogger(__name__)


class AbstractDataView(object):
    """
    AbstractDataView class docstring.  Defaults to a single matplotlib axes
    """

    default_dict_type = defaultdict
    default_list_type = list

    def __init__(self, data_list, key_list, *args, **kwargs):
        """
        Parameters
        ----------
        data_list : list
            The data stored as a list
        key_list : list
            The order of keys to plot
        """
        super(AbstractDataView, self).__init__(*args, **kwargs)

        if len(data_list) != len(key_list):
            raise ValueError(("lengths of data ({0}) and keys ({1}) must be the"
                              " same").format(len(data_list), len(key_list)))
        if data_list is None:
            raise ValueError(("data_list cannot have a value of None. It must "
                              "be, at minimum, an empty list"))
        if key_list is None:
            raise ValueError(("key_list cannot have a value of None. It must "
                              "be, at minimum, an empty list"))
        # init the data dictionary
        data_dict = self.default_dict_type()
        if len(data_list) > 0:
            # but only give it values if the data_list has any entries
            for (k, v) in zip(key_list, data_list):
                data_dict[k] = v

        # stash the dict and keys
        self._data_source = data_dict
        self._key_list = key_list

    def replot(self):
        """
        Do nothing in the abstract base class. Needs to be implemented
        in the concrete classes
        """
        raise NotImplementedError("Must override the replot() method in "
                                  "the concrete base class")

    def clear_data(self):
        """
        Clear all data
        """
        self._data_source.clear()
        self._key_list[:] = []

    def remove_data(self, lbl_list):
        """
        Remove the key:value pair from the dictionary as specified by the
        labels in lbl_list

        Parameters
        ----------
        lbl_list : list
            String
            name(s) of dataset to remove
        """
        for lbl in lbl_list:
            try:
                del self._data_source[lbl]
                self._key_list.remove(lbl)
            except KeyError:
                # do nothing
                pass


class AbstractDataView1D(AbstractDataView):
    """
    AbstractDataView1D class docstring.
    """

    # no init because AbstractDataView1D contains no new attributes

    def add_data(self, lbl_list, x_list, y_list, position=None):
        """
        add data with the name 'lbl'.  Will overwrite data if
        'lbl' already exists in the data dictionary

        Parameters
        ----------
        lbl : String
            Name of the data set
        x : np.ndarray
            single vector of x-coordinates
        y : np.ndarray
            single vector of y-coordinates
        position: int
            The position in the key list to begin inserting the data.
            Default (None) behavior is to append to the end of the list
        """
        # loop over the data passed in
        if position is None:
            position = len(self._key_list)
        for counter, (lbl, x, y) in enumerate(zip(lbl_list, x_list, y_list)):
            self._data_source[lbl] = (x, y)
            self._key_list.insert(position+counter, lbl)

    def append_data(self, lbl_list, x_list, y_list):
        """
        Append (x, y) coordinates to a dataset.  If there is no dataset
        called 'lbl', add the (x_data, y_data) tuple to a new entry
        specified by 'lbl'

        Parameters
        ----------
        lbl : list
            str
            name of data set to append
        x : list
            np.ndarray
            single vector of x-coordinates to add.
            x_data must be the same length as y_data
        y : list
            np.ndarray
            single vector of y-coordinates to add.
            y_data must be the same length as x_data
        """
        lbl_to_add = []
        x_to_add = []
        y_to_add = []
        for (lbl, x, y) in zip(lbl_list, x_list, y_list):
            lbl = str(lbl)
            if lbl in self._data_source:
                # get the current vectors at 'lbl'
                (prev_x, prev_y) = self._data_source[lbl]
                # set the concatenated data to 'lbl'
                self._data_source[lbl] = (np.concatenate((prev_x, x)),
                                        np.concatenate((prev_y, y)))
            else:
                # key doesn't exist, append the data to lists
                lbl_to_add.append(lbl)
                x_to_add.append(x)
                y_to_add.append(y)
        if len(lbl_to_add) > 0:
            self.add_data(lbl_list=lbl_to_add, x_list=x_to_add, y_list=y_to_add)


class AbstractDataView2D(AbstractDataView):
    """
    AbstractDataView2D class docstring
    """

    def __init__(self, data_list, key_list, *args, **kwargs):
        """
        Parameters
        ----------
        data_dict : Dict
            k:v pairs of data
        key_list : List
            ordered key list which defines the order that images appear in the
            stack
        corners_dict : Dict
            k:v pairs of the location of the corners of each image
            (x0, y0, x1, y1)
        """
        super(AbstractDataView2D, self).__init__(data_list=data_list,
                                                 key_list=key_list, *args,
                                                 **kwargs)

    def add_data(self, lbl_list, xy_list, corners_list=None, position=None):
        """
        add data with the name 'lbl'.  Will overwrite data if
        'lbl' already exists in the data dictionary

        Parameters
        ----------
        lbl : String
            Name of the data set
        x : np.ndarray
            single vector of x-coordinates
        y : np.ndarray
            single vector of y-coordinates
        position: int
            The position in the key list to begin inserting the data.
            Default (None) behavior is to append to the end of the list
        """
        # check for default corners_list behavior
        if corners_list is None:
            corners_list = self.default_list_type()
            for xy in xy_list:
                corners_list.append(self.find_corners(xy))
        # declare a local loop index
        counter = 0
        # loop over the data passed in
        for (lbl, xy, corners) in zip(lbl_list, xy_list, corners_list):
            # stash the data
            self._data_source[lbl] = xy
            # stash the corners
            self._corners_dict[lbl] = corners
            # insert the key into the desired position in the keys list
            if position is None:
                self._key_list.append(lbl)
            else:
                self._key_list.insert(i=position+counter, x=lbl)
                counter += 1

    def append_data(self, lbl_list, xy_list, axis=[], append_to_end=[]):
        """
        Append (x, y) coordinates to a dataset.  If there is no dataset
        called 'lbl', add the (x_data, y_data) tuple to a new entry
        specified by 'lbl'

        Parameters
        ----------
        lbl : list
            str
            name of data set to append
        xy : list
            np.ndarray
            List of 2D arrays
        axis : list
            int
            axis == 0 is appending in the horizontal direction
            axis == 1 is appending in the vertical direction
        append_to_end : list
            bool
            if false, prepend to the dataset
        """
        for (lbl, xy, ax, end) in zip(lbl_list, xy_list, axis, append_to_end):
            try:
                # set the concatenated data to 'lbl'
                if end:
                    self._data_source[lbl] = np.r_[str(ax),
                                                 self._data_source[lbl],
                                                 xy]
                    # TODO: Need to update the corners_list also...
                else:
                    self._data_source[lbl] = np.r_[str(ax),
                                                 xy,
                                                 self._data_source[lbl]]
                    # TODO: Need to update the corners_list also...
            except KeyError:
                # key doesn't exist, add data to a new entry called 'lbl'
                self.add_data(lbl, xy)

    def add_datum(self, lbl_list, x_list, y_list, val_list):
        """
        Add a single data point to an array

        Parameters
        ----------
        lbl : list
            str
            name of the dataset to add one datum to
        x : list
            int
            index of x coordinate
        y : list
            int
            index of y coordinate
        val : list
            float
            value of datum at the coordinates specified by (x,y)
        """
        raise NotImplementedError("Not yet implemented")
