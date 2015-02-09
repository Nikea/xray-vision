__author__ = 'edill'
import enaml
from .model import Plot1dModel
with enaml.imports():
    from .view import PlotView, PlotControls
