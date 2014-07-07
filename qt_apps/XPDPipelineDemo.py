'''
Created on Jun 18, 2014

@author: Eric-hafxb
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from matplotlib.backends.qt4_compat import QtGui, QtCore
import sys
import os
from vistools.qt_widgets.stack_scanner import StackScannerMainWindow
import numpy as np
from collections import OrderedDict
from vistools.qt_widgets.OneDimStack import OneDimStackMainWindow
from nsls2 import core
from nsls2.io.binary import read_binary


class data_gen_2d(object):
    def __init__(self, length, func=None):
        self._len = length
        nx = 2048
        ny = 2048
        self._x, self._y = [_ * 2 * np.pi / (ny / 2) for _ in
                            np.ogrid[-(nx / 2):(nx / 2), -(ny / 2):(ny / 2)]]
        self._rep = int(np.sqrt(length))

    def __len__(self):
        return self._len

    def __getitem__(self, k):
        kx = k // self._rep + 1
        ky = k % self._rep
        return np.sin(kx * self._x) * np.cos(ky * self._y) + 1.05

    @property
    def ndim(self):
        return 2

    @property
    def shape(self):
        len(self._x), len(self._y)


def get_files():
    files = QtGui.QFileDialog.getOpenFileNames(parent=None,
                                              caption="File opener")
    return files


def parse_files(files):
    lbls = []
    imgs = []
    if len(files) > 1:
        for afile in files:
            data, header = read_file(afile)
            lbls.append(str(afile))
            imgs.append(data)
    else:
        data, header = read_file(files)
        lbls.append(str(files))
        imgs.append(data)

    return lbls, imgs


def read_file(filename):
    # probably need to call a specific file reader here
    data, header = read_binary(filename=filename, nx=2048, ny=2048,
                               nz=1, dsize=np.uint16, headersize=0)

    return data, header


class Pipeline(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("XPD Pipeline Example")
        # init the 2d stack main window
        self._2ddata = data_gen_2d(25)
        self._2d = StackScannerMainWindow(parent=self, data_obj=self._2ddata)

        # init the 1d stack main window
        od = OrderedDict()
        img_idx = 1
        x_idx = 100
        od["init"] = (range(len(self._2ddata[img_idx][x_idx])),
                            self._2ddata[img_idx][x_idx])
        self._1d = OneDimStackMainWindow(data_dict=od)

        layout = QtGui.QHBoxLayout()

        layout.addWidget(self._2d)
        layout.addWidget(self._1d)

        # declare button to generate data for testing/example purposes
        self.btn_loaddata = QtGui.QPushButton("load data set",
                                        parent=self._1d._ctrl_widget)

        self.btn_loaddata.clicked.connect(self.open_data)
        ctrl_widget = self._2d._ctrl_widget.widget()
        ctrl_layout = ctrl_widget.layout()

        ctrl_layout.addWidget(QtGui.QLabel("--- File IO Buttons ---"))
        ctrl_layout.addWidget(self.btn_loaddata)

        # connect signals to test harness
        self.sig_add_real_data.connect(
            self._2d._widget.set_img_stack)

        # set the central widget layout
        self.central_widg = QtGui.QWidget(parent=self)
        self.central_widg.setLayout(layout)

        self.setCentralWidget(self.central_widg)

        # connect the data changed signal from the 2d viewer to the
        # analysis pipeline
        self._2d._widget.sig_data_changed.connect(
            self.sl_pipeline)
        # connect the output of the analysis to the 1d widget's receive data
        self.sig_pipe_done.connect(
            self._1d._widget._canvas.sl_add_data)

    # Qt Signals for Data loading
    sig_add_real_data = QtCore.Signal(list, list)
    sig_pipe_done = QtCore.Signal(list, list, list)

    @QtCore.Slot()
    def open_data(self):
        files = get_files()
        lbls, images = parse_files(files)
        self.sig_add_real_data.emit(lbls, images)

    @QtCore.Slot(np.ndarray, str)
    def sl_pipeline(self, img, name):
        center = (1020.208, 1033.321)
        x, y, img = core.detector2D_to_1D(img=img, detector_center=center)
        r = np.sqrt(x ** 2 + y ** 2)
        edges, val, count = core.bin_1D(x=r, y=img, min_x=0, max_x=50, bin_step=1)
        edges = edges[0:len(val)]
        print("length of (edges, val, count): ({0}, {1}, {2})".
              format(len(edges), len(val), len(count)))
        lbls = [name]
        x_data = [edges]
        y_data = [val / count]
        self.sig_pipe_done.emit(lbls, x_data, y_data)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Pipeline()
    window.show()
    sys.exit(app.exec_())
