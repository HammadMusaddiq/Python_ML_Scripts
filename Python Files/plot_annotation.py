import cv2
from PIL import Image
import numpy as np

im = Image.open('/home/hammad/Downloads/PakAustria_2D_Pix4d_transparent_mosaic_group1_3_3.tif')
numpy_array = np.asarray(im)
print(numpy_array.shape)

d = {
    "detections": [
        {
            "class": "civilian_vehicle",
            "confidence": 0.8546591401100159,
            "bbox": [
                1025.0,
                4909.967391967773,
                78.8348617553711,
                72.07704162597656
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.8444233536720276,
            "bbox": [
                1774.2817077636719,
                2168.4896240234375,
                75.95948791503906,
                148.38470458984375
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.8297598361968994,
            "bbox": [
                1800.5809631347656,
                1839.2672729492188,
                95.41903686523438,
                52.2049560546875
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.730671226978302,
            "bbox": [
                4734.002716064453,
                0.0,
                31.997283935546875,
                88.58464050292969
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.6827024221420288,
            "bbox": [
                1807.5813598632812,
                1915.7451171875,
                137.26251220703125,
                63.5308837890625
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.6542147397994995,
            "bbox": [
                572.0880279541016,
                2370.047561645508,
                152.33233642578125,
                62.17814636230469
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.65262770652771,
            "bbox": [
                1027.6465394496918,
                2307.8419151306152,
                62.3703978061676,
                123.93718338012695
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.6424669027328491,
            "bbox": [
                1848.078463792801,
                1925.7819366455078,
                91.14412379264832,
                54.5537109375
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.5794150829315186,
            "bbox": [
                1128.7841796875,
                2291.8690299987793,
                52.947052001953125,
                106.30252456665039
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.511788547039032,
            "bbox": [
                1640.0,
                2208.1084747314453,
                20.404287338256836,
                97.89152526855469
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.48073193430900574,
            "bbox": [
                1795.2269287109375,
                2006.393798828125,
                142.79461669921875,
                69.38609313964844
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.47502532601356506,
            "bbox": [
                1498.3195991516113,
                2212.041015625,
                59.11558151245117,
                81.58963012695312
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.44702422618865967,
            "bbox": [
                1683.2369346618652,
                2193.806350708008,
                58.06057357788086,
                86.089599609375
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.40341106057167053,
            "bbox": [
                820.0,
                2486.4542541503906,
                20.6626033782959,
                24.545745849609375
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.3802821934223175,
            "bbox": [
                3280.0606369040906,
                2385.7780151367188,
                20.44169196859002,
                17.746414184570312
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.3708798885345459,
            "bbox": [
                787.0778350830078,
                2303.7139053344727,
                58.470733642578125,
                131.72307586669922
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.3647013306617737,
            "bbox": [
                4895.002044677734,
                2255.0,
                75.35798645019531,
                119.59260559082031
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.3452025055885315,
            "bbox": [
                4086.492919921875,
                454.5012893676758,
                90.4228286743164,
                134.68889617919922
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.3056182265281677,
            "bbox": [
                1061.8476867675781,
                830.7011966705322,
                13.903213500976562,
                61.55531120300293
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.304378867149353,
            "bbox": [
                1663.5752410888672,
                3075.0,
                27.424758911132812,
                10.487677574157715
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "civilian_vehicle",
            "confidence": 0.30244389176368713,
            "bbox": [
                4100.544570922852,
                360.22813415527344,
                70.50077819824219,
                100.77186584472656
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "military_vehicle",
            "confidence": 0.6052849292755127,
            "bbox": [
                1596.219482421875,
                2203.23046875,
                66.4007568359375,
                134.940673828125
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "military_vehicle",
            "confidence": 0.5973547101020813,
            "bbox": [
                1273.23974609375,
                2204.495361328125,
                68.056884765625,
                143.79931640625
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "military_vehicle",
            "confidence": 0.4138992726802826,
            "bbox": [
                1026.244873046875,
                2304.228759765625,
                62.7626953125,
                119.150390625
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "military_vehicle",
            "confidence": 0.3595377206802368,
            "bbox": [
                785.8268432617188,
                2303.4169921875,
                56.53424072265625,
                125.0791015625
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "military_vehicle",
            "confidence": 0.32790496945381165,
            "bbox": [
                1028.9561524391174,
                410.0,
                132.01998281478882,
                114.47747039794922
            ],
            "inference_time": 28.60360622406006
        },
        {
            "class": "military_vehicle",
            "confidence": 0.32648220658302307,
            "bbox": [
                862.1610984802246,
                2618.4591522216797,
                98.23917007446289,
                48.38525390625
            ],
            "inference_time": 28.60360622406006
        }
    ],
    "label": [
        "civilian_vehicle",
        "military_vehicle"
    ],
    "object_count": {
        "civilian_vehicle": 21,
        "military_vehicle": 6
    }
}


annotated_image = numpy_array
annotated_boxes = d.get('detections')
for data in annotated_boxes:
    box = [int(val) for val in data.get('bbox')]
    label = data.get('class')

    annotated_image = cv2.rectangle(annotated_image, (box[0], box[1]), (box[2]+box[0], box[3]+box[1]), (255, 0, 0), 3)
    annotated_image = cv2.putText(annotated_image, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2)

cvt_Img = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", 1400, 800) # (w,h)
cv2.imshow("Image", cvt_Img)
cv2.waitKey(0)
cv2.destroyAllWindows()
