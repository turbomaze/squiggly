"""
Squiggly vision module
"""

from PIL import Image, ImageFilter
from skimage import io, transform, morphology
from skimage import color as skcolor
import numpy as np

NO_BLOB = -1
COLORS_TO_DETECT = {
    'R': [255, 0, 0],
    'G': [0, 255, 0],
    'B': [0, 0, 255]
}
MASK_COLOR = [255, 255, 255]
DESIRED_WIDTH = 500
LAB_THRESH = {
    'red': 40,
    'blue': 30,
    'green': 30
}
LAB_COLORS = {
    'red': [48.10022646, 71.47352807, 39.7632324],
    'green': [47.72064798, -31.10112263, 19.58122412],
    'blue': [26.61034757, 8.59396988, -28.84937727],
    'black': [0., 0., 0.],
    'white': [1.00000000e+02, -2.45493786e-03, 4.65342115e-03]
}


# assumes image at filename is from a phone and rotated
def get_image_data(filename):
    rgb = io.imread(filename)
    if rgb.shape[0] > DESIRED_WIDTH:
        height = int(
            DESIRED_WIDTH * (rgb.shape[1]/float(rgb.shape[0]))
        )
        rgb = transform.resize(rgb, (DESIRED_WIDTH, height))
    lab = skcolor.rgb2lab(rgb)
    return transform.rotate(lab, -90.0)


# image is a {size: (w, h), data: [...]} type of thing
def get_pillow_image(image):
    pillow_image = Image.new('RGB', image['size'])
    pillow_image.putdata(image['data'])
    return pillow_image


# mutates a LAB image into perfect rgb
def rgbify(image):
    def dist(a, b):
        return (
            (a[0]-b[0])**2 +
            (a[1]-b[1])**2 +
            (a[2]-b[2])**2
        ) ** 0.5

    data = []
    for i in range(image.shape[0]):
        data.append([])
        for j in range(image.shape[1]):
            c = image[i][j]
            if dist(c, LAB_COLORS['red']) < LAB_THRESH['red']:
                data[i].append([255, 0, 0])
            elif dist(c, LAB_COLORS['green']) < LAB_THRESH['green']:
                data[i].append([0, 255, 0])
            elif dist(c, LAB_COLORS['blue']) < LAB_THRESH['blue']:
                data[i].append([0, 0, 255])
            else:
                data[i].append([0, 0, 0])
    return np.array(data, dtype=np.uint8)


# returns image of True/False (white/black)
def blackandwhited(image):
    bw = []
    for i in range(image.shape[0]):
        bw.append([])
        for j in range(image.shape[1]):
            smallest = min(image[i][j])
            biggest = max(image[i][j])
            median = sum(image[i][j]) - biggest - smallest
            if smallest == 0 and median == 0 and biggest == 255:
                bw[i].append(True)
            else:
                bw[i].append(False)
    return np.array(bw)


def bw_to_rgb(image):
    rgb = []
    for i in range(image.shape[0]):
        rgb.append([])
        for j in range(image.shape[1]):
            if image[i][j]:
                rgb[i].append([255, 255, 255])
            else:
                rgb[i].append([0, 0, 0])
    return np.array(rgb, dtype=np.uint8)


def get_mask_from_rgbed(rgbed):
    bwed = blackandwhited(rgbed)

    # dilate
    dilated = morphology.binary_dilation(
        morphology.binary_dilation(bwed)
    )
    dilated_image = bw_to_rgb(dilated)
    return dilated_image


'''
Detects blobs of a given color in an image.

@param image numpy array image
@param blob_color the color to blob in the image, a 3-tuple
       of RGB values
@return a list of blobs, each of which is a set of (x, y)
        points that occur in the blob
'''
def detect_blobs(image, blob_color):
    height, width, _ = image.shape

    # get location information of the pixels
    all_pixels = []
    for i in range(height):
        for j in range(width):
            all_pixels.append((list(image[i][j]), j, i))

    # only keep pixels that are the blob color
    relevant_pixels = filter(
        lambda pixel: pixel[0] == blob_color,
        all_pixels
    )

    # keep track of where each pixel in all_pixels went to
    pixel_dict = {}
    for i, pixel in enumerate(relevant_pixels):
        idx = width * pixel[2] + pixel[1]
        pixel_dict[idx] = i

    # the initial blob ids of each pixel
    blob_ids = [NO_BLOB] * len(relevant_pixels)

    current_id = NO_BLOB + 1  # next number

    for i in range(len(relevant_pixels)):
        # if the pixel is already in a blob, skip it
        if blob_ids[i] != NO_BLOB:
            continue

        blob_ids[i] = current_id

        q = [i]
        while len(q) > 0:
            current = q.pop(0)
            _, x, y = relevant_pixels[current]
            change_queue = []
            if x + 1 < width:
                el = y * width + x + 1
                change_queue.append(el)
            if x - 1 >= 0:
                el = y * width + x - 1
                change_queue.append(el)
            if y - 1 >= 0:
                el = (y - 1) * width + x
                change_queue.append(el)
            if y + 1 < height:
                el = (y + 1) * width + x
                change_queue.append(el)

            for change_idx in change_queue:
                if change_idx in pixel_dict:
                    # location is idx in relevant_pixels
                    location = pixel_dict[change_idx]
                    if blob_ids[location] == NO_BLOB:
                        blob_ids[location] = current_id
                        q.append(location)

        current_id += 1

    blobs = {}
    for i, blob_id in enumerate(blob_ids):
        if blob_id not in blobs:
            blobs[blob_id] = set()

        _, x, y = relevant_pixels[i]
        blobs[blob_id].add((x, y))

    blob_sets = blobs.values()
    return blob_sets

'''
Gets the centroid of a blob.

@param  blob --  dictionary object with keys 'type' that maps to a string
                representing the blob's color and 'points' that maps to
                a set of tuples (x,y)
@return x,y coordinates of center of the blob as a tuple
'''
def get_blob_centroid(blob):
    x_coords = [float(pt[0]) for pt in blob['points']]
    y_coords = [float(pt[1]) for pt in blob['points']]
    center = (int(round(sum(x_coords)) / len(x_coords)), int(round(sum(y_coords) / len(y_coords))))
    return center

'''
Gets block ids and origins given the mask blobs and color id blobs.

@param mask_blobs - blobs detected by getting blobs on a mask of the image
@param color_id_blobs - blobs detected by getting blobs for each color id
'''
def get_block_ids_and_origins(mask_blobs, color_id_blobs):
    blocks = []

    # Loop through each mask blob and through each color id blob
    for mask_blob in mask_blobs:
        color_blobs_in_mask_blob = []

        for color_id_blob in color_id_blobs:
            centroid = get_blob_centroid(color_id_blob)

            # If the center of the color id blob is in the mask blob,
            # store the information in a list, color_blobs_in_mask_blob
            if centroid in mask_blob['points']:
                color_blobs_in_mask_blob.append({
                    'type': color_id_blob['type'],
                    'center': centroid
                })
        # Sort the color_blobs_in_mask_blob by the x coordinate of the center.
        color_blobs_in_mask_blob.sort(key=lambda x: x['center'][0])

        # Create the block id by concatenating the blob's type (color)
        block_id = ''
        for blob in color_blobs_in_mask_blob:
            block_id += blob['type']

        # Adding to a list of blocks the id and origin of the block
        blocks.append({
            'id': block_id,
            'origin': get_blob_centroid(mask_blob)
        })

    return blocks


def process(filename):
    # load the image, resized and in LAB space
    image = get_image_data(filename)

    # rgbify all of the colors
    rgbed = rgbify(image)
    print 'rgbed'

    # get the mask
    dilated_image = get_mask_from_rgbed(rgbed)
    print 'masked'

    # blobs of all of the RGB colors
    all_color_blobs = []
    for color_name in COLORS_TO_DETECT:
        color = COLORS_TO_DETECT[color_name]
        # blobs of a single color
        color_blobs = detect_blobs(rgbed, color)
        all_color_blobs.extend(map(
            lambda color_blob: {
                'type': color_name,
                'points': color_blob
            },
            color_blobs
        ))

    # blobs of the masks
    mask_blobs = map(
        lambda blob: {
            'type': MASK_COLOR,
            'points': blob
        },
        detect_blobs(dilated_image, MASK_COLOR)
    )

    # get the block ids
    info = get_block_ids_and_origins(mask_blobs, all_color_blobs)
    print info

    # save it
    io.imsave('rgbed.png', rgbed)
    io.imsave('dilated.png', dilated_image)
    print 'done'
