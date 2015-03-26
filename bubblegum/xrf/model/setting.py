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
from __future__ import (absolute_import, division,
                        print_function)

__author__ = 'Li Li'

import six
import numpy as np
from collections import OrderedDict

from atom.api import (Atom, Str, observe, Typed,
                      Dict, List, Int, Enum, Float, Bool)

from skxray.constants.api import XrfElement as Element

import logging
logger = logging.getLogger(__name__)


class ROIModel(Atom):
    """
    This class defines basic data structure for roi calculation.

    Attributes
    ----------
    prefix : str
        prefix name
    line_val : float
        emission energy of primary line
    left_val : float
        left boundary
    right_val : float
        right boundary
    default_left : float
    default_right : float
    step : float
        min step value to change
    show_plot : bool
        option to plot
    """
    prefix = Str()
    line_val = Int()
    left_val = Int()
    right_val = Int()
    default_left = Int()
    default_right = Int()
    step = Int(1)
    show_plot = Bool(False)

    @observe('left_val')
    def _value_update(self, change):
        if change['type'] == 'create':
            return
        logger.debug('left value is changed {}'.format(change))

    @observe('show_plot')
    def _plot_opt(self, change):
        if change['type'] == 'create':
            return
        logger.debug('show plot is changed {}'.format(change))


class SettingModel(Atom):
    """
    Control roi calculation according to given inputs.

    Parameters
    ----------
    parameters : dict
        parameter values used for fitting
    data_dict : dict
        dict of 3D data
    prefix_name_roi : str
        name ID for roi calculation
    element_for_roi : str
        inputs given by users
    element_list_roi : list
        list of elements after parsing
    roi_dict : dict
        dict of ROIModel object
    """
    parameters = Dict()
    data_sets = Dict()

    prefix_name_roi = Str()
    element_for_roi = Str()
    element_list_roi = List()
    roi_dict = OrderedDict()

    @observe('element_for_roi')
    def _update_element(self, change):
        """
        Get element information as a string and parse it as a list.
        This element information means the ones for roi setup.
        """
        self.element_for_roi = self.element_for_roi.strip(' ')
        if len(self.element_for_roi) == 0:
            logger.warning('No elements enetered.')
            self.remove_all_roi()
            self.element_list_roi = []
            return
        elif ',' in self.element_for_roi:
            element_list = [v.strip(' ') for v in self.element_for_roi.split(',')]
        else:
            element_list = [v for v in self.element_for_roi.split(' ')]

        #with self.suppress_notifications():
        #    self.element_list_roi = element_list
        logger.warning('Current elements are: {}'.format(element_list))
        self.update_roi(element_list)
        self.element_list_roi = element_list

    def remove_all_roi(self):
        self.roi_dict.clear()

    def update_roi(self, element_list, std_ratio=2):
        """
        Update elements without touching old ones.

        Parameters
        ----------
        element_list : list
            list of elements for roi
        std_ratio : float, optional
            Define the range of roi for given element.

        Notes
        -----
        The unit of energy is in ev in this function. The reason is
        SpinBox in Enaml can only read integer as input. To be updated.
        """
        for v in element_list:
            if self.roi_dict.has_key(v):
                continue

            if '_K' in v:
                temp = v.split('_')[0]
                e = Element(temp)
                val = int(e.emission_line['ka1']*1000)
            elif '_L' in v:
                temp = v.split('_')[0]
                e = Element(temp)
                val = int(e.emission_line['la1']*1000)
            elif '_M' in v:
                temp = v.split('_')[0]
                e = Element(temp)
                val = int(e.emission_line['ma1']*1000)

            delta_v = int(self.get_sigma(val/1000)*1000)
            roi = ROIModel(prefix=self.prefix_name_roi,
                           line_val=val,
                           left_val=val-delta_v*std_ratio,
                           right_val=val+delta_v*std_ratio,
                           default_left=val-delta_v*std_ratio,
                           default_right=val+delta_v*std_ratio,
                           step=1,
                           show_plot=False)

            self.roi_dict.update({v: roi})

    @observe('prefix_name_roi')
    def _update_prefix(self, change):
        if change['type'] == 'create':
            return
        logger.info('Use prefix name : {}'.format(self.prefix_name_roi))
        for k, v in six.iteritems(self.roi_dict):
            v.prefix = self.prefix_name_roi

    def get_sigma(self, energy, epsilon=2.96):
        """
        Calculate the std at given energy.
        """
        temp_val = 2 * np.sqrt(2 * np.log(2))
        return np.sqrt((self.parameters['fwhm_offset'].value/temp_val)**2 +
                       energy*epsilon*self.parameters['fwhm_fanoprime'].value)

    def get_roi_sum(self):
        """
        Save roi sum into a dict.

        Returns
        -------
        dict
            nested dict as output
        """
        roi_result = {}
        for fname, datav in six.iteritems(self.data_sets):
            fname = fname.split('.')[0]
            temp = {}
            for k, v in six.iteritems(self.roi_dict):
                lowv = v.left_val/1000
                rightv = v.right_val/1000
                sum2D = calculate_roi(datav.raw_data, self.parameters['e_linear'].value,
                                      self.parameters['e_offset'].value, [lowv, rightv])
                temp.update({k: sum2D})
                logger.info('Calculation is done for {}, {}, {}'.format(v.prefix, fname, k))
            roi_result.update({v.prefix+'_'+fname: temp})
        return roi_result


def calculate_roi(data3D, e_linear, e_offset, range_v):
    """
    Calculate 2D map for given ROI.

    Parameters
    ----------
    data3D : 3D array
    e_linear : float
    e_offset : float
    range_v : list

    Returns
    -------
    array
        2D map
    """
    data3D = np.asarray(data3D)
    range_v = np.asarray(range_v)
    range_v = (range_v - e_offset)/e_linear
    range_v = [int(round(v)) for v in range_v]
    #return np.sum(data3D[range_v[0]:range_v[1], :, :], axis=0)*e_linear
    return np.sum(data3D[:, :, range_v[0]:range_v[1]], axis=2) * e_linear
