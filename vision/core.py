"""
Squiggly vision module
"""

from PIL import Image
from sets import Set

BITS_PER_CHANNEL = 8


def get_image_data(filename):
    image = Image.open(filename)
    return {
        'size': image.size,
        'data': list(image.getdata())
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


def posterize_color(color, bits):
    # map doesn't work on tuples
    return (
        posterize_channel(color[0], bits),
        posterize_channel(color[1], bits),
        posterize_channel(color[2], bits),
    )


def posterize_channel(value, bits):
    return (value >> bits) << bits


def foobar(filename):
    image = get_image_data(filename)
    posterized = get_pillow_image(posterize(image, 1))
    posterized.save('swag.png')


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
            if centroid in mask_blob:
                a.append({
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
            'id': blob_id,
            'origin': get_blob_centroid(mask_blob)
        })

    return blocks


mask_blobs = {
    'type': 'BLACK',
    'points': Set([(0,0), (1,0), (2,0), (3,0), (0,1), (1,1), (2,1)])
}
color_id_blobs = []
color_id_blobs.append({
    'type': 'R',
    'points': Set([(0,1), (1,1), (1,0), (2,0)])
})
color_id_blobs.append({
    'type': 'G',
    'points': Set([(0,0)])
})

blocks = get_block_ids_and_origins(mask_blobs, color_id_blobs)
print blocks


