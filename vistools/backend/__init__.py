from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import defaultdict

from six.moves import zip
import numpy as np

__author__ = 'Eric-hafxb'


class AbstractDataView(object):
    """
    AbstractDataView class docstring.  Defaults to a single matplotlib axes
    """

    default_dict_type = defaultdict
    default_list_type = list

    def __init__(self, data_dict=None, key_list=None, *args, **kwargs):
        """
        Parameters
        ----------
        data_dict : Dict
            The data stored in k:v pairs
        key_list : list
            The order of keys to plot
        """
        super(AbstractDataView, self).__init__(*args, **kwargs)
        # generate a key list that corresponds to the entries in the data
        # dictionary if no key_list was passed in
        if data_dict is not None and key_list is None:
            key_list = list(data_dict.keys())

        # otherwise, set defaults if required
        if data_dict is None:
            data_dict = self.default_dict_type()
        if key_list is None:
            key_list = self.default_list_type()

        # stash the dict and keys
        self._data_dict = data_dict
        self._key_list = key_list

    def replot(self):
        """
        Do nothing in the abstract base class. Needs to be implemented
        in the concrete classes
        """
        raise Exception("Must override the replot() method in the concrete base class")

    def clear_data(self):
        """
        Clear all data
        """
        self._data_dict.clear()
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
                del self._data_dict[lbl]
                del self._key_list[lbl]
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
        # declare a local loop index
        counter = 0
        # loop over the data passed in
        for (lbl, x, y) in zip(lbl_list, x_list, y_list):
            self._data_dict[lbl] = (x, y)
            if position is None:
                self._key_list.append(lbl)
            else:
                self._key_list.insert(i=position+counter, x=lbl)
                counter += 1

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
            if self._data_dict.has_key(lbl):
                # get the current vectors at 'lbl'
                (prev_x, prev_y) = self._data_dict[lbl]
                # set the concatenated data to 'lbl'
                self._data_dict[lbl] = (np.concatenate((prev_x, x)),
                                   np.concatenate((prev_y, y)))
            else:
                # key doesn't exist, append the data to lists
                lbl_to_add.append(lbl)
                x_to_add.append(x)
                y_to_add.append(y)
        if lbl_to_add is not None:
            self.add_data(lbl_list=lbl_to_add, x_list=x_to_add, y_list=y_to_add)


class AbstractDataView2D(AbstractDataView):
    """
    AbstractDataView2D class docstring
    """

    def __init__(self, data_dict=None, key_list=None, corners_dict=None, *args,
                 **kwargs):
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
        super(AbstractDataView2D, self).__init__(data_dict=data_dict,
                                                 key_list=key_list, *args,
                                                 **kwargs)
        # handle default behavior for corners_list
        if corners_dict is None and data_dict is not None:
            corners_dict = self.default_dict_type()
            for key in data_dict.keys():
                corners_dict[key] = self.find_corners(data_dict[key])

        # stash the corners dict
        self._corners_dict = corners_dict

    def find_corners(self, xy_data):
        """
        Find the corners of all images in the data_dict

        Parameters
        ----------
        xy_data : np.ndarray
            Array to determine the corners of

        Return
        ------
        This is just (x0, y0, x1, y1) = (0, 0, int(data_dict[key].shape))
        """
        x, y = xy_data.shape
        return 0, 0, int(x), int(y)

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
            self._data_dict[lbl] = xy
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
                    self._data_dict[lbl] = np.r_[str(ax), self._data_dict[lbl], xy]
                    # TODO: Need to update the corners_list also...
                else:
                    self._data_dict[lbl] = np.r_[str(ax), xy, self._data_dict[lbl]]
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