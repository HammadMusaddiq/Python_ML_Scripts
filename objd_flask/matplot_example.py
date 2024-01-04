from skimage import io as io_skimage
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

img = io_skimage.imread('http://192.168.18.33/osint_system/media_files/lap.jpg') # img in numpy

# To plot image from numpy with Skimage
# io_skimage.imshow(img)
# plt.show()

# To plot image from numpy with Matplotlib
fig = plt.figure()
#plt.imshow(img) 
# plt.show() # image object
#print(plt) # numpy array

# First need to draw Figure
fig.canvas.draw_image(img)
#fig.canvas.draw()
# Now we can save it to a numpy array.
data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
#print(data)

# canvas = FigureCanvasAgg(fig)
# canvas.draw()
# buf = fig.canvas.tostring_rgb()
# ncols, nrows = fig.canvas.get_width_height()
# img_canvas_arr = np.frombuffer(buf, dtype=np.uint8).reshape(nrows, ncols, 3)
# print(img_canvas_arr)

plt.imshow(data)
plt.show()

# fig, ax = plt.subplots(figsize=(14,12),facecolor='Black')
# ax.imshow(img)
# print(ax)