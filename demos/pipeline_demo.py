from __future__ import print_function
from datetime import datetime
from bubblegum.pipeline import (DataMuggler, PipelineComponent,
                       MuggleWatcherLatest, MuggleWatcherTwoLists
                       )
import time
import numpy as np
import matplotlib.pyplot as plt
from nsls2 import core
from bubblegum import QtCore
from bubblegum.backend.mpl.cross_section_2d import (absolute_limit_factory,
                                                    CrossSection)


def plotter(title, xlabel, ylabel):
    fig, ax = plt.subplots(1, 1)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    txt = ax.annotate('', (0, 0), xytext=(1, 1), xycoords='axes fraction')
    ln, = ax.plot([], [])
    time_tracker = {'old': time.time()}

    def inner(y, x):
        ln.set_data(x, y)
        ax.relim()
        ax.autoscale_view(False, True, True)
        cur = time.time()
        txt.set_text(str(cur - time_tracker['old']))
        time_tracker['old'] = cur
        ax.figure.canvas.draw()
        #        plt.pause(.1)

    return inner


def imshower():
    fig = plt.figure()
    xsection = CrossSection(fig,
                frame_source.gen_next_frame(), interpolation='none',
                limit_func=absolute_limit_factory((0, 1.5))
                )

    def inner(msg, data):
        xsection.update_image(data['img'])

    return inner


# stolen from other live demo
class FrameSourcerBrownian(QtCore.QObject):
    event = QtCore.Signal(object, dict)

    def __init__(self, im_shape, step_scale=1, decay=30,
                 delay=500, parent=None):
        QtCore.QObject.__init__(self, parent)
        self._im_shape = np.asarray(im_shape)
        self._scale = step_scale
        self._decay = decay
        self._delay = delay
        if self._im_shape.ndim != 1 and len(self._im_shape) != 2:
            raise ValueError("image shape must be 2 dimensional "
                             "you passed in {}".format(im_shape))
        self._cur_position = np.array(np.asarray(im_shape) / 2)

        self.timer = QtCore.QTimer(parent=self)
        self.timer.timeout.connect(self.get_next_frame)
        self._count = 0

    @QtCore.Slot()
    def get_next_frame(self):
        print('fired {}'.format(self._count))
        if not self._count % 50:
            self._scale += .5
            self.event.emit(datetime.now(), {'T': self._scale})
        self._count += 1
        im = self.gen_next_frame()
        self.event.emit(datetime.now(), {'img': im, 'count': self._count})

        return True

    def gen_next_frame(self):
        # add a random step
        self._cur_position += np.random.randn(2) * self._scale
        # clip it
        self._cur_position = np.array([np.clip(v, 0, mx) for
                                       v, mx in zip(self._cur_position,
                                                    self._im_shape)])

        R = core.pixel_to_radius(self._im_shape,
                                 self._cur_position).reshape(self._im_shape)
        im = (np.exp((-R**2 / self._decay)) *
              (1 + .5*np.sin(self._count * np.pi / 15)))
        return im

    @QtCore.Slot()
    def start(self):
        self.timer.start(self._delay)

    @QtCore.Slot()
    def stop(self):
        self.timer.stop()

# used below
img_size = (150, 150)
frame_source = FrameSourcerBrownian(img_size, delay=200, step_scale=.5)


# set up mugglers
dm = DataMuggler((('T', 'pad', True),
                  ('img', 'bfill', False),
                  ('count', 'bfill', True)
                  )
                 )
dm2 = DataMuggler((('T', 'pad', True),
                   ('mean', 'bfill', True),
                   ('x', 'bfill', True),
                   ('y', 'bfill', True),
                   ('count', 'bfill', True)
                   )
                  )
# construct a watcher for the image + count on the main DataMuggler
mw = MuggleWatcherLatest(dm, 'img', ['count', ])

# set up pipe line components
# multiply the image by 5 because we can
p1 = PipelineComponent(lambda msg, data: (msg,
                                          {'img': data['img'] * 5,
                                           'count': data['count']}))

# find the mean and estimate (badly) the center of the blob
p2 = PipelineComponent(lambda msg, data: (msg,
                                          {'mean':
                                             np.mean(data['img']),
                                          'count': data['count'],
                                          'x': np.mean(np.argmax(data['img'],
                                                                 axis=0)),
                                          'y': np.mean(np.argmax(data['img'],
                                                                 axis=1)),
                                          }))


# hook up everything
# input
frame_source.event.connect(dm.append_data)
# first DataMuggler in to top of pipeline
mw.sig.connect(p1.sink_slot)
# p1 output -> p2 input
p1.source_signal.connect(p2.sink_slot)
# p2 output -> dm2
p2.source_signal.connect(dm2.append_data)


# connect the cross section viewer to the first DataMuggler
mw.sig.connect(imshower())

# construct a watcher + viewer of the mean
mw3 = MuggleWatcherTwoLists(dm2, 'count', 'mean', 'count')
mw3.sig.connect(plotter("average intensity", "frame #", 'mean'))

# construct a watcher + viewer of the center
mw4 = MuggleWatcherTwoLists(dm2, 'count', 'y', 'x')
mw4.sig.connect(plotter('center', 'x', 'y'))

# construct a watcher + viewer of the temperature
mw5 = MuggleWatcherTwoLists(dm, 'count', 'T', 'count')
mw5.sig.connect(plotter('Temperature', 'count', 'T'))


frame_source.start()
plt.show(block=True)
