"""
Squiggly vision module
"""

from PIL import Image

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
