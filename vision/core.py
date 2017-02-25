"""
Squiggly vision module
"""

from PIL import Image, ImageDraw, ImageFilter, ImageTk


def get_image_data(filename):
    image = Image.open(filename)
    return list(image.getdata())


def foobar(filename):
    data = get_image_data(filename)
    print data
    return 'processing image'
