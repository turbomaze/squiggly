"""
Squiggly vision module
"""

from PIL import Image, ImageDraw, ImageFilter, ImageTk


def get_image_data(filename):
    image = Image.open(filename)
    return {
        'size': image.size,
        'data': list(image.getdata())
    }


def posterize(image):
    width = image.size[0]
    print width


def foobar(filename):
    image = get_image_data(filename)
    print image.size
