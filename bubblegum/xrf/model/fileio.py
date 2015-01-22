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

__author__ = 'Li Li'

import numpy as np
import os
import logging
logger = logging.getLogger(__name__)

from atom.api import Atom, Str, observe, Typed, Dict, List, Int


class FileIOModel(Atom):
    """
    This class focuses on file input and output.

    Attributes
    ----------
    working_directory : str
    data_file : str
    data : array
        Experiment data.
    file_path : str
    load_status : str
        Description of file loading status
    """
    #folder_name = Str(folder)
    file_name = Str(file)
    file_names = List()
    data = Typed(np.ndarray)
    #file_path = Str(data_path)
    file_path = Str()
    path_list = List()

    working_directory = Str()
    data_file = Str()
    data = Typed(np.ndarray)

    load_status = Str()
    file_opt = Int()
    data_dict = Dict()

    def __init__(self, working_directory=None, data_file=None, *args, **kwargs):
        if working_directory is None:
            working_directory = os.path.expanduser('~')

        with self.suppress_notifications():
            self.working_directory = working_directory
            self.data_file = data_file
        # load the data file
        self.load_data()

    @observe('working_directory', 'data_file')
    def path_changed(self, changed):
        if changed['type'] == 'create':
            return
        self.load_data()

    @observe('data')
    def data_changed(self, changed):
        print('The data was changed. First five lines of new data:\n{}'
              ''.format(self.data[:5]))

    def load_data(self):
        """
        This function needs to be updated to handle other data formats.
        """
#<<<<<<< HEAD
        #try:
        self.file_path = os.path.join(self.working_directory, self.data_file)
        self.data = np.loadtxt(self.file_path)
        #self.load_status = 'File {} is loaded successfully.'.format(self.file_name)
        #except IOError:
        #    self.load_status = 'File {} doesn\'t exist.'.format(self.file_name)
        #except ValueError:
        #    self.load_status = 'File {} can\'t be loaded. '.format(self.file_name)

    @observe('file_names')
    def update_more_data(self, changed):
        for fname in self.file_names:
            try:
                self.file_path = os.path.join(self.working_directory, fname)
                self.load_data()
                self.file_name = fname
                self.data_dict.update({fname: self.data.copy()})
            except ValueError:
                continue

            #self.pathlist.append(self.file_path)
        print('all keys: {}'.format(self.data_dict.keys()))

    @observe('file_opt')
    def choose_file(self, changed):
        print('option is {}'.format(self.file_opt))
        if self.file_opt == 0:
            return
        self.file_name = self.file_names[self.file_opt-1]
        #self.file_path = os.path.join(self.folder_name, fname)
        self.data = self.data_dict[str(self.file_name)]

        # file_path = os.path.join(self.working_directory, self.data_file)
        # try:
        #     self.data = np.loadtxt(file_path)
        #     self.load_status = 'File {} is loaded successfully.'.format(self.data_file)
        # except IOError:
        #     self.load_status = 'File {} doesn\'t exist.'.format(self.data_file)
        # except ValueError:
        #     self.load_status = 'File {} can\'t be loaded. '.format(self.data_file)