from PIL import Image
import ctypes
import numpy as np
import cv2

class Grayscale:
    CHARACTERS = (' ', '·', '∘', '◦', '•', '●', '░', '▒', '▓', '█')
    # SYMBOL_RATIO = 0.55
    SYMBOL_RATIO = 0.42

    def __init__(self, max_width = 80, max_height: int = 20, force_width = None, mirror: bool = False) -> None:
        self.max_width = max_width
        self.max_height = max_height
        self.force_width = force_width
        self.mirror = mirror

        self.image_string = ctypes.create_unicode_buffer('')

        self.chars_count = len(self.CHARACTERS)

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

        return self.image_string.value

    def cv2(self, frame: np.ndarray, width, height):
        resized_frame: np.ndarray = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        gray_frame: np.ndarray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        if self.mirror:
            gray_frame = cv2.flip(gray_frame,1)

        pixels = gray_frame.flatten()

        self.pixels(pixels, width, height)

        return self.image_string.value

    def resize(self, width: int, height: int) -> tuple[int, int]:
        aspect_ratio = height/width
        new_width = self.max_width if width > self.max_width else width
        if self.force_width is not None:
            new_width = self.force_width
        new_height = int(aspect_ratio * new_width * self.SYMBOL_RATIO)
        if new_height > self.max_height:
            new_height = self.max_height
            new_width = int(new_height / aspect_ratio / self.SYMBOL_RATIO)

        row = ''.rjust(new_width)
        image_string = '\n'.join([
            row for _ in range(new_height)
        ])
        self.image_string = ctypes.create_unicode_buffer(image_string)

        return new_width, new_height

    def pixels(self, pixels: tuple|np.ndarray, width: int, height: int) -> None:
        pixels_count = len(pixels)

        symbol_col = -1
        for row_index in range(0, pixels_count, width):
            next_row_index = row_index+width
            for col_index in range(row_index, next_row_index):
                symbol_col += 1
                pixel = pixels[col_index]
                symbol = self.CHARACTERS[round(pixel * self.chars_count / 255) - 1]
                self.image_string[symbol_col] = symbol
            symbol_col += 1
