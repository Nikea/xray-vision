__author__ = 'edill'

import enaml
from enaml.qt.qt_application import QtApplication
from xray_vision.xrf.model.xrf_model import XRF

def run():
    app = QtApplication()
    with enaml.imports():
        from xray_vision.xrf.view.file_view import FileGui

    view = FileGui()
    view.xrf_model1 = XRF()
    view.xrf_model2 = XRF()

    view.show()
    app.start()


if __name__ == "__main__":
    run()
