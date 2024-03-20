import argparse
import shutil

from PIL import Image

from blackwhite import BlackWhite
from grayscale import Grayscale
from rgba import RGBA

def get_args():
    size = shutil.get_terminal_size((80, 20))

    parser = argparse.ArgumentParser(description='Image to ASCII converter')

    parser.add_argument('image', type=str,
                    help='Path to image')
    parser.add_argument('--max_width', type=int, default=size.columns,
                    help='Maximum width to resize bigger image to in symbols. Default to COLUMNS')
    parser.add_argument('--force_width', type=int,
                    help='Width to resize image to in symbols even if image is smaller. Default to image width or COLUMNS')
    parser.add_argument('--max_height', type=int, default=size.lines,
                    help='Maximum height to resize bigger image to in symbols. Default to LINES')
    parser.add_argument('--converter', type=str, default='grayscale',
                        choices=['grayscale', 'rgba', '4blackwhite'],
                        help='Converter to use. One of: grayscale (default), rgba, 4blackwhite (x4 resolution)')
    parser.add_argument('--mirror', action='store_true',
                    help='Mirror image')

    return parser.parse_args()

def main():
    args = get_args()

    image = Image.open(args.image)

    force_width = args.force_width
    max_width = args.max_width
    max_height = args.max_height
    converter = args.converter
    mirror = args.mirror

    if converter == 'grayscale':
        driver = Grayscale(max_width=max_width, max_height=max_height, force_width=force_width, mirror=mirror)
    elif converter == '4blackwhite':
        driver = BlackWhite(max_width=max_width, max_height=max_height, force_width=force_width, mirror=mirror)
    elif converter == 'rgba':
        driver = RGBA(max_width=max_width, max_height=max_height, force_width=force_width, mirror=mirror)
    else:
        raise Exception('Unsupported Converter')

    ascii = driver.pil(image)
    print(ascii, end=None)

if __name__ == "__main__":
    main()
