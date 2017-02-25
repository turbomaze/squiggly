"""
Squiggly vision module
"""

from PIL import Image, ImageDraw, ImageFilter, ImageTk


def get_image_data(filename):
    image = Image.open(filename)
    return (image.size, list(image.getdata()))


def foobar(filename):
    image = get_image_data(filename)
    print image[0]
