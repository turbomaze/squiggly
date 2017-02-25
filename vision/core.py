"""
Squiggly vision module
"""

from PIL import Image, ImageFilter
from skimage import io
from skimage import color as skcolor
import numpy as np

NO_BLOB = -1
BITS_PER_CHANNEL = 8
COLORS_TO_DETECT = {
    'R': (255, 0, 0),
    'G': (0, 255, 0),
    'B': (0, 0, 255)
}
DESIRED_WIDTH = 1000
FILTER_SIZE = 7
BLUE_TO_ADD = 70
LAB_THRESHOLD = 70

LAB_COLORS = {
    'red': [48.10022646, 71.47352807, 39.7632324],
    'green': [47.72064798, -31.10112263, 19.58122412],
    'blue': [26.61034757, 8.59396988, -28.84937727],
    'black': [0., 0., 0.],
    'white': [1.00000000e+02, -2.45493786e-03, 4.65342115e-03]
}


def get_image_data(filename):
    rgb = io.imread(filename)
    lab = skcolor.rgb2lab(rgb)

    return lab


def get_blurred_data(filename):
    pil_image = get_pillow_image(get_image_data(filename))
    blurred = pil_image.filter(
        ImageFilter.MedianFilter(FILTER_SIZE)
    )
    even_more_blurred = blurred.filter(
        ImageFilter.GaussianBlur(FILTER_SIZE)
    )
    return {
        'size': even_more_blurred.size,
        'data': list(even_more_blurred.getdata())
    }


# image is a {size: (w, h), data: [...]} type of thing
def get_pillow_image(image):
    pillow_image = Image.new('RGB', image['size'])
    pillow_image.putdata(image['data'])
    return pillow_image


def posterize(image, bits_to_preserve):
    bits_to_remove = BITS_PER_CHANNEL - bits_to_preserve
    new_data = map(
        lambda color: posterize_color(color, bits_to_remove),
        image['data']
    )
    return {
        'size': image['size'],
        'data': new_data
    }


def add_color_to_pixels(image, color_to_add):
    new_data = map(
        lambda color: (
            color[0] + color_to_add[0],
            color[1] + color_to_add[1],
            color[2] + color_to_add[2]
        ),
        image['data']
    )
    return {
        'size': image['size'],
        'data': new_data
    }


# keeps colors that are basically RGB and set others to black
def rgbify(image):
    new_data = []
    for color in image['data']:
        if color_is_extreme(color):
            max_color = [0, 0, 0]
            max_color[get_max_channel(color)] = 255
            new_data.append(tuple(max_color))
        else:
            new_data.append((0, 0, 0))

    return {
        'size': image['size'],
        'data': new_data
    }


def posterize_color(color, bits):
    # map doesn't work on tuples
    return (
        posterize_channel(color[0], bits),
        posterize_channel(color[1], bits),
        posterize_channel(color[2], bits),
    )


def posterize_channel(value, bits):
    return (value >> bits) << bits


'''
Detects blobs of a given color in an image.

@param image Image of the form {'size': ..., 'data': [...]}
@param blob_color the color to blob in the image, a 3-tuple
       of RGB values
@return a list of blobs, each of which is a set of (x, y)
        points that occur in the blob
'''
def detect_blobs(image, blob_color):
    width, height = image['size']

    # get location information of the pixels
    all_pixels = map(
        lambda (i, color): (color, i % width, i / width),
        enumerate(image['data'])
    )

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
    print blob_ids
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
    # image = get_blurred_data(filename)
    # rgbed = get_pillow_image(
    #     rgbify(posterize(
    #         image, 1
    #     ))
    # )
    # rgbed.save('rgbed.png')
    image = get_image_data(filename)
    print(image.shape)

    def dist(a, b):
        return (
            (a[0]-b[0])**2 +
            (a[1]-b[1])**2 +
            (a[2]-b[2])**2
        ) ** 0.5

    shape = image.shape
    for i in range(shape[0]):
        for j in range(shape[1]):
            color = image[i][j]
            if dist(color, LAB_COLORS['blue']) > LAB_THRESHOLD:
                image[i][j] = np.array(LAB_COLORS['black'])
            else:
    ugh = skcolor.lab2rgb(image)
    io.imsave('sexy.png', ugh)
