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
#from . import QtCore
from matplotlib.backends.qt_compat import QtCore

import pandas as pd


class PipelineComponent(QtCore.QObject):
    """
    The top-level object to represent a component in the quick-and-dirty
    live-data pipe line.

    WARNING these docs do not match what is written, but are what _should_
    be written.  currently the message is serving as the index which should
    probably be packed in with the data or as it own arguement.  In either
    case need to talk to the controls group before spending the effort to
    re-factor.

    This class provides the basic machinery for the signal and
    slot required for the hooking up the pipeline.

    The processing function needs to be provided at instatiation:

        def process_msg(message, data_object):
            # do stuff with message/data
            return result_message, result_data

    This function can also return `None` to indicate that there is no
    output for further processing.

    The scheme for managing/schema of the content of the messages will be
    pinned down at a later date.

    Currently this scheme does no checking to ensure types are correct or
    valid pre-running

    Parameters
    ----------
    process_function : callable
        Must have the following signature:

        def process_msg(message, data_object):
            # do stuff with message/data
            return result_message, result_data
            # return None

    """
    source_signal = QtCore.Signal(object, object)

    def __init__(self, process_function, **kwargs):
        super(PipelineComponent, self).__init__(**kwargs)
        self._process_msg = process_function

    @QtCore.Slot(object, object)
    def sink_slot(self, message, data_payload):
        """
        This function is the entry point for pushing data through
        this node in the pipeline.

        Parameters
        ----------
        timestamp : datetime or sequence of datetime
            The timestamp that aligns with the data in the data payload

        data_payload : object
            dict of lists or something that looks like it.


        """
        try:
            ret = self._process_msg(message, data_payload)
        except Exception as E:
            # yes, gotta catch 'em all!!
            print("something failed")
            print(E)
        else:
            if ret is not None:
                self.source_signal.emit(*ret)


class DataMuggler(QtCore.QObject):
    """
    This class provides a wrapper layer of signals and slots
    around a pandas DataFrame to make plugging stuff in for live
    view easier.

    The data collection/event model being used is all measurements
    (that is values that come off of the hardware) are time stamped
    to ring time.  The assumption that there will be one measurement
    (ex an area detector) which can not be interpolated and will serve
    as the source of reference time stamps.

    The language being used through out is that of pandas data frames.
    The data model is that of a sparse table keyed on time stamps which
    is 'densified' on demand by propagating the last measured value forward.



    Parameters
    ----------
    col_spec : list
        List of information about the columns. Each entry should
        be a tuple of the form (name, nafill_mode, is_scalar)

    """

    # this is a signal emitted when the muggler has new data that
    # clients can grab.  The list return is the names of the columns
    # that have new data
    new_data = QtCore.Signal(list)

    def __init__(self, col_spec, **kwargs):
        super(DataMuggler, self).__init__(**kwargs)
        valid_na_fill = {'pad', 'ffill', 'bfill', 'backpad'}

        self._fill_methods = dict()
        self._nonscalar_lookup = dict()
        self._is_not_scalar = set()
        names = []
        for c_name, fill_method, is_scalar in col_spec:
            # validate fill methods
            if fill_method not in valid_na_fill:
                raise ValueError(("{} is not a valid fill method "
                                 "must be one of {}").format(fill_method,
                                                             valid_na_fill))
            # used to sort out which way filling should be done.
            # forward for motor-like, backwards from image-like
            self._fill_methods[c_name] = fill_method
            # determine if the value should be stored directly in the data
            # frame or in a separate data structure
            if not is_scalar:
                self._is_not_scalar.add(c_name)
                self._nonscalar_lookup[c_name] = dict()
            names.append(c_name)

        # make an empty data frame
        self._dataframe = pd.DataFrame({n: [] for n in names}, index=[])

    def append_data(self, time_stamp, data_dict):
        """
        Add data to the DataMuggler.

        Parameters
        ----------
        time_stamp : datetime or list of datetime
            The times of the data

        data_dict : dict
            The keys must be a sub-set of the columns that the DataMuggler
            knows about.  If `time_stamp` is a list, then the values must be
            lists of the same length, if `time_stamp` is a single datatime
            object then the values must be single values
        """
        if not all(k in self._dataframe for k in data_dict):
            # TODO dillify this error checking
            raise ValueError("trying to pass in invalid key")
        try:
            iter(time_stamp)
        except TypeError:
            # if time_stamp is not iterable, assume it is a datetime object
            # and we only have one data point to deal with so up-convert
            time_stamp = [time_stamp, ]
            data_dict = {k: [v, ] for k, v in six.iteritems(data_dict)}

        # deal with non-scalar look up magic
        for k in data_dict:
            # if non-scalar shove tha data into the storage
            # and replace the data with the id of the value object
            # this should probably be a hash, but this is quick and dirty
            if k in self._is_not_scalar:
                ids = []
                for v in data_dict[k]:
                    ids.append(id(v))
                    self._nonscalar_lookup[k][id(v)] = v
                data_dict[k] = ids

        # make a new data frame with the input data and append it to the
        # existing data
        self._dataframe = self._dataframe.append(
            pd.DataFrame(data_dict, index=time_stamp))
        self._dataframe.sort(inplace=True)
        # emit that we have new data!
        self.new_data.emit(list(data_dict))

    def get_values(self, reference_column, other_columns, time_range=None):
        """
        Return a dictionary of data resampled (filled) to the times which have
        non-NaN values in the reference column

        Parameters
        ----------
        reference_column : str
            The 'master' column to get time stamps from

        other_columns : list of str
            A list of the other columns to return

        time_range : tuple or None
            Times to limit returned data to.  This is not implemented.

        Returns
        -------
        index : list
            Nominally the times of each of data points

        out_data : dict
            A dictionary of the
        """
        if time_range is not None:
            raise NotImplementedError("you can only get all data right now")

        # grab the times/index where the primary key has a value
        index = self._dataframe[reference_column].dropna().index
        # make output dictionary
        out_data = dict()
        # for the keys we care about
        for k in [reference_column, ] + other_columns:
            # pull out the DataSeries
            work_series = self._dataframe[k]
            # fill in the NaNs using what ever method needed
            work_series = work_series.fillna(method=self._fill_methods[k])
            # select it only at the times we care about
            work_series = work_series[index]
            # if it is not a scalar, do the look up
            if k in self._is_not_scalar:
                out_data[k] = [self._nonscalar_lookup[k][t]
                               for t in work_series]
            # else, just turn the series into a list so we have uniform
            # return types
            else:
                out_data[k] = list(work_series.values)

        # return the index an the dictionary
        return list(index), out_data

    def get_last_value(self, reference_column, other_columns):
        """
        Return a dictionary of the dessified row an the most recent
        time where reference column has a valid value

        Parameters
        ----------
        reference_column : str
            The 'master' column to get time stamps from

        other_columns : list of str
            A list of the other columns to return

        time_range : tuple or None
            Times to limit returned data to.  This is not implemented.

        Returns
        -------
        index : Timestamp
            The time associated with the data

        out_data : dict
            A dictionary of the
        """
        # grab the times/index where the primary key has a value
        index = self._dataframe[reference_column].dropna().index
        # make output dictionary
        out_data = dict()
        # for the keys we care about
        for k in [reference_column, ] + other_columns:
            # pull out the DataSeries
            work_series = self._dataframe[k]
            # fill in the NaNs using what ever method needed
            work_series = work_series.fillna(method=self._fill_methods[k])
            # select it only at the times we care about
            work_series = work_series[index]
            # if it is not a scalar, do the look up
            if k in self._is_not_scalar:
                out_data[k] = self._nonscalar_lookup[k][work_series.values[-1]]

            # else, just turn the series into a list so we have uniform
            # return types
            else:
                out_data[k] = work_series.values[-1]

        # return the index an the dictionary
        return index[-1], out_data


class MuggleWatcherLatest(QtCore.QObject):
    """
    This is a class that watches DataMuggler's for the `new_data` signal, grabs
    the lastest row (filling in data from other rows as needed) at the columns
    selected.  You probably should not extract columns which fill back as they
    will come out as NaN in this (I think).

    Parameters
    ----------
    muggler : DataMuggler
        The mugger to keep tabs on

    watch_column : str
        The name of the comlumn to watch for additions to

    extract_columns : list of str
        Additional columns to extract in addition to the watched column

    """
    # signal to emit index + data
    sig = QtCore.Signal(object, dict)

    def __init__(self, muggler, watch_column, extract_colums, **kwargs):
        super(MuggleWatcherLatest, self).__init__(**kwargs)
        self._muggler = muggler
        self._ref_col = watch_column
        self._other_cols = extract_colums
        self._muggler.new_data.connect(self.process_message)

    @QtCore.Slot(list)
    def process_message(self, updated_cols):
        """
        Process the updates from the muggler to see if there
        is anything we need to deal with.

        Parameters
        ----------
        updated_cols : list
            Updated columns

        """
        if self._ref_col in updated_cols:
            ind, res_dict = self._muggler.get_last_value(self._ref_col,
                                                         self._other_cols)
            self.sig.emit(ind, res_dict)


class MuggleWatcherTwoLists(QtCore.QObject):
    """
    This class watches a DataMuggler and when it gets new data extracts
    all of the time series data, for two columns and emits both as lists
    """
    sig = QtCore.Signal(list, list)

    def __init__(self, muggler, watch_col, col1, col2, **kwargs):
        super(MuggleWatcherTwoLists, self).__init__(**kwargs)
        self._muggler = muggler
        self._ref_col = watch_col
        self._other_cols = [col1, col2]
        self._muggler.new_data.connect(self.process_message)

    @QtCore.Slot(list)
    def process_message(self, updated_cols):
        """
        Process the updates from the muggler to see if there
        is anything we need to deal with.

        Parameters
        ----------
        updated_cols : list
            Updated columns

        """
        if self._ref_col in updated_cols:
            ind, res_dict = self._muggler.get_values(self._ref_col,
                                                         self._other_cols)
            self.sig.emit(res_dict[self._other_cols[0]],
                          res_dict[self._other_cols[1]])


class MuggleWatcherAll(QtCore.QObject):
    """
    This class watches a DataMuggler and when it gets new data extracts
    all of the time series data, not just the latest.
    """
    sig = QtCore.Signal(list, dict)

    def __init__(self, muggler, watch_column, extract_colums, **kwargs):
        super(MuggleWatcherAll, self).__init__(**kwargs)
        self._muggler = muggler
        self._ref_col = watch_column
        self._other_cols = extract_colums
        self._muggler.new_data.connect(self.process_message)

    @QtCore.Slot(list)
    def process_message(self, updated_cols):
        """
        Process the updates from the muggler to see if there
        is anything we need to deal with.

        Parameters
        ----------
        updated_cols : list
            Updated columns

        """
        if self._ref_col in updated_cols:
            ind, res_dict = self._muggler.get_values(self._ref_col,
                                                         self._other_cols)
            self.sig.emit(ind, res_dict)
