import matplotlib
from skimage import draw as skd
import matplotlib.pyplot as plt
import xray_vision.mpl_plotting as xrv_plt
import numpy as np

import skxray.roi as roi

frame_shape = (128, 128)

test_image = np.zeros(frame_shape)
r = 5

for n, (i, j) in enumerate(zip([5, 15, 40, 110],
                               [120, 10, 50, 80]), 1):
    rr, cc = skd.circle(i, j, r, shape=frame_shape)
    test_image[rr, cc] = n


fig, ax = plt.subplots()
xrv_plt.roi.show_label_array(ax, test_image)

# make some sample data
x = np.linspace(-2, 2, 100)
X, Y = np.meshgrid(x, x)
Z = 100*np.cos(np.sqrt(x**2 + Y**2))**2 + 50

inner_radius = 10   # radius of the first ring
width = 4           # width of each ring
spacing = 4         # no spacing between rings
num_rings = 3       # number of rings
center = (50, 50)   # center of the image

#  find the edges of the required rings
edges = roi.ring_edges(inner_radius, width, spacing, num_rings)

# create a label array
rings = roi.rings(edges, center, Z.shape)

fig, ax = plt.subplots()
xrv_plt.roi.show_label_array_on_image(ax, Z, rings)
