from PIL import Image
import numpy as np
import cv2
import ctypes

class BlackWhite:
    CHARACTERS = {
            0x0000: ' ',
            0x1100: '▀',
            0x0011: '▄',
            0x1111: '█',
            0x1010: '▌',
            0x0101: '▐',
            0x0010: '▖',
            0x0001: '▗',
            0x1000: '▘',
            0x1011: '▙',
            0x1001: '▚',
            0x1110: '▛',
            0x1101: '▜',
            0x0100: '▝',
            0x0110: '▞',
            0x0111: '▟',
    }
    SYMBOL_RATIO = 0.42
    MIDDLE_SHADE = 100

    def __init__(self, max_width: int = 80, max_height: int = 20, force_width: int|None = None, mirror: bool = False) -> None:
        self.max_width = max_width
        self.max_height = max_height
        self.force_width = force_width
        self.mirror = mirror

        self.image_string = ctypes.create_unicode_buffer('')

    def pil(self, image: Image.Image):
        width, height = image.size

        image = image.resize(self.resize(width, height))

        width, height = image.size

        # convert image to greyscale format
        image = image.convert('L')

        if self.mirror:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        pixels = tuple(image.getdata())

        self.pixels(pixels, width, height)

        return str.rstrip(self.image_string.value, '\0')

    def cv2(self, frame: np.ndarray, width, height):
        resized_frame: np.ndarray = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        gray_frame: np.ndarray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        if self.mirror:
            gray_frame = cv2.flip(gray_frame,1)

        pixels = gray_frame.flatten()

        self.pixels(pixels, width, height)

        return str.rstrip(self.image_string.value, '\0')

    def resize(self, width: int, height: int) -> tuple[int, int]:
        aspect_ratio = height/width
        row_width = self.max_width if width > self.max_width else width
        if self.force_width is not None:
            row_width = self.force_width
        new_width = row_width * 2
        new_height = int(aspect_ratio * new_width * self.SYMBOL_RATIO)
        if new_height > (self.max_height * 2):
            new_height = self.max_height * 2
            new_width = int(new_height / aspect_ratio / self.SYMBOL_RATIO)
            row_width = int((new_width - 1)/ 2)

        row = ''.rjust(row_width + 1)
        image_string = '\n'.join([
            row for _ in range(int(new_height / 2))
        ])
        self.image_string = ctypes.create_unicode_buffer(image_string)

        return new_width, new_height

    def pixels(self, pixels: tuple|np.ndarray, width: int, height: int) -> None:
        pixels_count = len(pixels)

        rows_per_line = 2
        cols_per_symbol = 2
        line_width = rows_per_line*width
        symbol_col = -1
        for row_index in range(0, pixels_count, line_width):
            next_row_index = row_index+width
            next_line_index = next_row_index+width
            for col in range(row_index, next_row_index, cols_per_symbol):
                symbol_col += 1
                key = 0x0000
                i = col
                if pixels[i] < self.MIDDLE_SHADE:
                    key |= 0x1000
                i += 1
                if i < next_row_index and pixels[i] < self.MIDDLE_SHADE:
                    key |= 0x0100
                try:
                    i = col+width
                    if pixels[i] < self.MIDDLE_SHADE:
                        key |= 0x0010
                    i += 1
                    if i < next_line_index and pixels[i] < self.MIDDLE_SHADE:
                        key |= 0x0001
                except IndexError:
                    # if current row is the last
                    pass
                symbol = self.CHARACTERS[key]
                self.image_string[symbol_col] = symbol
            symbol_col += 1
