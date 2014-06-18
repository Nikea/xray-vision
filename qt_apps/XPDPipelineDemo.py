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
import nsls2


class data_gen_2d(object):
    def __init__(self, length, func=None):
        self._len = length
        self._x, self._y = [_ * 2 * np.pi / 500 for _ in
                            np.ogrid[-500:500, -500:500]]
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
    files = QtGui.QFileDialog.getOpenFileName(parent=None,
                                              caption="File opener")
    for afile in files:
        print(str(afile))
    return files


def parse_files(files):
    lbls = []
    imgs = []
    if os.path.isdir(files):
        for afile in files:
            f = open(afile, 'r')
            x, y = read_file(f)
            lbls.append(str(afile))
            imgs.append(x)
    else:
        f = open(files, 'r')
        x, y = read_file(f)
        lbls.append(str(files))
        imgs.append(x)

    return lbls, imgs


def read_file(afile):
    # probably need to call a specific file reader here
    data, header = nsls2.io.binary.read_binary(filename=afile, nx=2048, ny=2048,
                                dsize=np.uint16, headersize=0)

    return data


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
            self._2d._widget._canvas.sl_update_image)

        # set the central widget layout
        self.central_widg = QtGui.QWidget(parent=self)
        self.central_widg.setLayout(layout)

        self.setCentralWidget(self.central_widg)

    # Qt Signals for Data loading
    sig_add_real_data = QtCore.Signal(list, list)

    @QtCore.Slot()
    def open_data(self):
        files = get_files()
        self.sig_add_real_data.emit(*parse_files(files))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Pipeline()
    window.show()
    sys.exit(app.exec_())
