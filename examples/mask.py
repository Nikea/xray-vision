from __future__ import print_function, division

import numpy as np
from skimage import data
import matplotlib.pyplot as plt
from xray_vision.mask.manual_mask import ManualMask

image = data.coins()

f, ax = plt.subplots()
f.canvas.mpl_disconnect(f.canvas.manager.key_press_handler_id)
f.canvas.manager.key_press_handler_id = None
mc = ManualMask(ax, image)
plt.show()

mask = mc.mask
regs = mc.label_array

print("masking {:.3f}% of the image".format(100 * np.sum(mask) / mask.size))
n_regs = np.max(regs)
out = np.bincount(regs.ravel())

for i in range(1, n_regs + 1):
    print("region {}: {} pixels".format(i, out[i]))
