import requests
import matplotlib.pyplot as plt
from matplotlib import patches, text, patheffects
import matplotlib as mpl
import random
from ftplib import FTP

from skimage import io as io_skimage

image_url = "https://st2.depositphotos.com/3591429/5245/i/950/depositphotos_52459259-stock-photo-group-of-busy-people-working.jpg"

img = io_skimage.imread(image_url)
# try:
    # if isinstance(image_output, str):     # if object plotted on the image then the return value will be the url of ftp in string
    #     results["urls"].append(image_output)
    # else: # if no object found in the image then image url will be same of input image

response = requests.post(f"http://{'10.100.103.200'}:{'5002'}/", json={"imageUrl":image_url})
objd = response.json()["data"]
print(objd)

# labels_list = response.json()["label"]
# confidence_list = response.json()["confidence"]
# bbox_list = response.json()["bbox"]
colors  = ['antiquewhite', 'aqua', 'aquamarine', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'forestgreen', 'fuchsia', 'gainsboro', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey', 'hotpink', 'indianred', 'indigo', 'khaki', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lime', 'limegreen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'yellow', 'yellowgreen']

def plot_Image_Boundings(objd_data,img):
    # converting str list to flost list
    objd_data_predicted_axis = []
    for axis in objd_data['predicted_axis']:
            objd_data_predicted_axis.append([float(val) for val in axis])
    if objd_data_predicted_axis: # If object(s) found in the image
        fig = plt.figure(figsize=(14,12),facecolor='Black')
        ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], alpha=1.0)
        ax.set_frame_on(False)
        ax.set_xticks([])
        ax.set_yticks([])
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
        for axis,b_text,b_color in zip(box_axis,box_text,box_color):
            for rectangle in axis:
                ax.add_patch(rectangle)
            text_x,text_y,text_s = b_text
            t = ax.text(text_x, text_y, text_s, verticalalignment='top', color="white", fontsize=8, weight='bold')
            t.set_bbox(dict(facecolor=b_color, alpha=0.4, edgecolor='black'))
            t.set_path_effects([patheffects.withStroke(linewidth=1,foreground="black")])
        ax.get_xaxis().set_visible(False)
        ax.imshow(img)
        # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # cv2.imshow('', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # plt.imshow(img)
        # plt.show()
        image = fig
        plt.close(fig)
        return image
        # ftp_url = ftp_image_url(image)  # fig has image object
        # return ftp_url
    else:  # If no object found in the image, img is numpy array of actual image
        return img


image_output = plot_Image_Boundings(objd[0], img)

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from PIL import Image
import io
from datetime import datetime

canvas = FigureCanvas(image_output)
canvas.draw()       # draw the canvas, cache the renderer
image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
print(image.shape)

image_from_plot = image.reshape(image_output.canvas.get_width_height()[::-1] + (3,))
print(image_from_plot.shape)

# plt.imshow(image_from_plot)
# plt.axis('off')
# plt.show()



node_ip_ftp = "10.100.103.114"
node_port_ftp = 21
auth_user_ftp = "micrcrawler"
auth_pass_ftp = "rapidev"

ftp = FTP(host=node_ip_ftp, user=auth_user_ftp, passwd= auth_pass_ftp)
base_url = "http://"+node_ip_ftp+"/osint_system/media_files/"


print("############# Image to FTP ##############")


# FTP Image URL
def ftp_image_url(ftp, image):
    # Image Name Based on Current Time and Random Number.
    ran_number = random.getrandbits(25)
    var_date = "Img"+str(datetime.now().timestamp()).replace(".","")
    img_name = str(var_date) + "_" + str(ran_number) + ".jpeg"    
    image_link = imageToFTP(ftp, "/WeaponObjectDetection", img_name, image)
    return image_link


ftp_image_url(ftp, image_from_plot)


def imageToFTP(ftp, path, file_name, image):
    if str(type(image)) == "<class 'numpy.ndarray'>": # if image type is numpy array
        image_rgb = Image.fromarray(np.uint8(image)).convert('RGB')
        image_bytes = io.BytesIO() 
        image_rgb.save(image_bytes, format="png") 
        image_bytes.seek(0)
    
    else:
        image_bytes = io.BytesIO() # This is a file object
        image.savefig(image_bytes, format="jpeg",bbox_inches='tight',pad_inches = 0) # Save the content to temp
        image_bytes.seek(0) # Re
    
    print('Uploading Image to FTP')
    if not is_connected():
        retry_ftp_connection()
        change_ftp_present_working_dir(path)
    else:
        change_ftp_present_working_dir(path)
    
    try:
        baseurl = base_url # ('str' object has no attribute 'copy')

        for p in path.split('/')[1:]:
            baseurl = baseurl + str(p) + "/"
        
        ftp_file_url = baseurl + file_name
        
        ftp.storbinary("STOR " + file_name , image_bytes)
        ftp.quit()
        
        print("Image saved on Ftp URL: "+str(ftp_file_url))
        print('Finished with success')

        return ftp_file_url

    except Exception as E:
        print("something went wrong... Reason: {}".format(E))
        return False




print("############# FTP Functions ##############")

def change_ftp_present_working_dir(ftp, pwd_path):
    try:
        if ftp.pwd() != pwd_path:
            ftp.cwd(pwd_path) #if error on changing cwd then make in exception
    except:
        try:
            for folder in pwd_path.split('/')[1:]:
                chdir(ftp, folder)
        except Exception as E:
            print("An Exception occured in while changing directory in FTP : {}".format(E)) 

def retry_ftp_connection(ftp):
    is_connected = False
    for i in range(5): # 5 retries
        if connect(ftp) == True:
            print("Connection established with FTP")
            if login(ftp) == True:
                print("Login with FTP successful")
                is_connected = True
                return is_connected
        else:
            error = "FTP Connection Error"
            E = ftp.connect()
            print("{} Reason: {}".format(error,E))
    
    return is_connected


def is_connected(ftp):
    try:
        ftp.pwd()
        return True
    except:
        return False
    
    
def connect(ftp):
    try:
        print("Trying FTP Connection ({}:{})".format(node_ip_ftp,node_port_ftp))
        ftp.connect(host=node_ip_ftp)
        return True
    except Exception as E:
        print("FTP Connect Error {}".format(E))
        return E

def login(ftp):
    try:
        ftp.login(auth_user_ftp, auth_pass_ftp)
        return True
    except Exception as E:
        return E

def directory_exists(ftp, dir):
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    return False

def chdir(ftp, dir):
    if directory_exists(ftp, dir) is False:
        ftp.mkd(dir)
    ftp.cwd(dir)

