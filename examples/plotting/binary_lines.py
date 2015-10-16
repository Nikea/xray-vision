import matplotlib.pyplot as plt
import xray_vision.mpl_plotting as xrv_plt
import numpy as np
from collections import OrderedDict


syn_data = OrderedDict()
for j in range(21):
    key = 'data {:02d}'.format(j)
    syn_data[key] = np.cumsum(np.random.randint(1, 10, 20)).reshape(-1, 2)

fig, ax = plt.subplots(tight_layout=True)
ret = xrv_plt.binary_state_lines(ax, syn_data, xmin=0, xmax=120)
plt.show()
