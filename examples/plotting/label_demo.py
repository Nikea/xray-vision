from skimage import draw as skd
import matplotlib.pyplot as plt
import xray_vision.mpl_plotting as xrv_plt
import numpy as np

frame_shape = (128, 128)

test_image = np.zeros(frame_shape)
r = 5

for n, (i, j) in enumerate(zip([5, 15, 40, 110],
                               [120, 10, 50, 80]), 1):
    rr, cc = skd.circle(i, j, r, shape=frame_shape)
    test_image[rr, cc] = n


fig, ax = plt.subplots()
xrv_plt.show_label_array(ax, test_image)
