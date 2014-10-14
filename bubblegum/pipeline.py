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
from . import QtCore


class PipelineComponent(QtCore.QObject):
    """
    The top-level object to represent a component in the quick-and-dirty
    live-data pipe line.

    This class provides the basic machinery for the signal and slot required for
    the hooking up the pipeline.

    This is meant to be sub-classed and sub classes must implement _process_msg
    which must have the signature::

        def _process_msg(self, message, data_object):
            return result_message, result_data

    This function can also return `None`

    The scheme for managing the messages will be pinned down at a later date.

    Currently this scheme does no checking to ensure types are correct or
    valid pre-running
    """
    source_signal = QtCore.Signal(str, object)

    @QtCore.Slot(str, object)
    def sink_slot(self, message, data_payload):
        """
        This function is the entry point for pushing data through
        this node in the pipeline.

        Parameters
        ----------
        message : str
            Some sort of string describing what the incoming data is

        data_payload : object
            The data to be processed.


        """
        try:
            ret = self._process_msg(message, data_payload)
        except Exception as E:
            # yes, catch them all!!
            print(E)
        else:
            if ret is not None:
                self.source_signal.emit(*ret)
