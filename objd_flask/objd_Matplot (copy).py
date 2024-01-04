import time
from black import T
import cv2, os
from cv2 import imshow
from matplotlib import patches, text, patheffects
import matplotlib.colors as mcolors 
from skimage import io
import matplotlib.pyplot as plt
import requests
import random
import math
import matplotlib.patheffects as PathEffects
import matplotlib as mpl

colors  = ['antiquewhite', 'aqua', 'aquamarine', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'forestgreen', 'fuchsia', 'gainsboro', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey', 'hotpink', 'indianred', 'indigo', 'khaki', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lime', 'limegreen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'yellow', 'yellowgreen']

node_ip_objd = '192.168.18.24'
node_port_objd = '5002'

#image_url = "http://192.168.18.33/osint_system/media_files/ess/st_fb_425/54377b03-4c61-481a-acb2-967dd58926ad.jpg"
image_url = "http://192.168.18.33/osint_system/media_files/cars.jpeg"

start = time.time()

response = requests.post(f"http://{node_ip_objd}:{node_port_objd}/", json={"imageUrl":image_url})
objd = response.json()["data"]

end = time.time()
print("Elapsed time for getting response: "+ str(end-start))
start1 = time.time()

#print(objd)
#print(type(objd))
objd_data = objd[0]

#print(objd_data)

objd_data_predicted_axis = []
for axis in objd_data['predicted_axis']:
    objd_data_predicted_axis.append([float(val) for val in axis])

objd_data_predicted_score = objd_data['probability_score']

objd_data_predicted_class = objd_data['object_classified']

# print(objd_data_predicted_score)

img = io.imread(image_url)

fig, ax = plt.subplots(figsize=(14,14))
plt.subplots_adjust(wspace=0, hspace=0)
fig.tight_layout()

box_axis = []
box_text = []
box_color = []
for _box,_score,_class in zip(objd_data_predicted_axis,objd_data['probability_score'],objd_data['object_classified']):
    x1, y1, x2, y2 = tuple(_box)    # xmin, ymin, xmax, ymax (x is Top, y is Left)
    # print(x1,y1,x2,y2)
    w, h = x2 - x1, y2 - y1  # width (w) = xmax - xmin ; height (h) = ymax - ymin (w is Right, h is Bottom)

    random_color = colors[random.randrange(0,len(colors) - 1)]
    box_color.extend([random_color])
    box_axis.append([mpl.patches.Rectangle((x1,y1),w,h, fill=False, color=random_color, lw=3)])
    box_text.append([x1+2, (y1+2), str(_class+' ('+_score+'%)')])

# print(box_axis[0])
# print(box_text[0])
# print(box_color)

#adding patches to axes
for axis,b_text,b_color in zip(box_axis,box_text,box_color):
    for rectangle in axis:
        ax.add_patch(rectangle)

    text_x,text_y,text_s = b_text
    t = ax.text(text_x, text_y, text_s, verticalalignment='top', color="white", fontsize=8, weight='bold')
    t.set_bbox(dict(facecolor=b_color, alpha=0.4, edgecolor='black'))
    t.set_path_effects([PathEffects.withStroke(linewidth=1,foreground="black")])
    
ax.get_xaxis().set_visible(False)
ax.imshow(img)


#plt.clf()
#plt.close()

#plt.imshow(fig)
#plt.show()

# plt.axis('off')
# plt.savefig("/home/dani/Downloads/abc.png",bbox_inches='tight')

# input("press enter to exit")

end1 = time.time()
print("Elapsed time for ploting objects: " + str(end1 - start1))
print("Total Time for a single image:" + str(end1-start))



# def plot_Image_Boundings(objd_data,img,image_size):
#     # converting str list to flost list
#     objd_data_predicted_axis = []
#     for axis in objd_data['predicted_axis']:
#         objd_data_predicted_axis.append([float(val) for val in axis])

#     height, width = image_size
#     # Pixels to Inches for Matplotlib
#     height = height * 0.0104166667
#     width = width * 0.0104166667

#     fig = plt.figure(figsize=(height,width),facecolor='Black')
#     ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], alpha=1.0)
#     ax.set_frame_on(False)
#     ax.set_xticks([])
#     ax.set_yticks([])
#     for _box,_score,_class in zip(objd_data_predicted_axis,objd_data['probability_score'],objd_data['object_classified']):
#         x1, y1, x2, y2 = tuple(_box)    # xmin, ymin, xmax, ymax (x is Top, y is Left)
#         w, h = x2 - x1, y2 - y1  # width (w) = xmax - xmin ; height (h) = ymax - ymin (w is Right, h is Bottom)
#         ax.imshow(img)
#         color = colors[random.randrange(0,len(colors) - 1)]
#         ax.add_patch(patches.Rectangle((x1,y1),w,h, fill=False, color=color, lw=3))
#         t = ax.text(x1+2,(y1+2),str(_class+' ('+_score+'%)'),verticalalignment='top',color="white",fontsize=8,weight='bold')
#         t.set_bbox(dict(facecolor=color, alpha=0.4, edgecolor='black'))
#         t.set_path_effects([PathEffects.withStroke(linewidth=1,foreground="black")])
#         #ax.clf()
#         # plt.clf()
#         # plt.close()

#     return fig  # fig has image object (RGB)