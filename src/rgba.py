from typing import NewType, Tuple
import numpy as np
import cv2

RGBAPixel = NewType("RGBAPixel", Tuple[int, int, int, int])
RGBPixel = NewType("RGBPixel", Tuple[int, int, int])
BGRPixel = NewType("BGRPixel", Tuple[int, int, int])


class RGBA:
    # CHARACTERS = ('█', '▓', '▒', '░', '●', '•', '◦', '∘', '·', ' ')
    CHARACTERS = (" ", "·", "∘", "◦", "•", "●", "░", "▒", "▓", "█")
    SYMBOL_RATIO = 0.42
    ALPHA_THRESHOLD = 10

    RGB_FOREGROUND = "\033[38;2;%d;%d;%dm"
    RESET = "\033[0m"

    TYPE_RGB = 0
    TYPE_BGR = 1

    def __init__(
        self,
        max_width=80,
        max_height: int = 20,
        force_width=None,
        mirror: bool = False,
        type=None,
    ) -> None:
        self.max_width = max_width
        self.max_height = max_height
        self.force_width = force_width
        self.mirror = mirror

        self.image_string = ""

        self.chars_count = len(self.CHARACTERS)

        if type == None:
            self.type = self.TYPE_RGB
        else:
            self.type = type

    def cv2(self, frame: np.ndarray, width, height):
        resized_frame: np.ndarray = cv2.resize(
            frame, (width, height), interpolation=cv2.INTER_LINEAR
        )

        if self.mirror:
            resized_frame = cv2.flip(resized_frame, 1)

        return self.rows(resized_frame)

    def resize(self, width: int, height: int) -> tuple[int, int]:
        aspect_ratio = height / width
        new_width = self.max_width if width > self.max_width else width
        if self.force_width is not None:
            new_width = self.force_width
        new_height = int(aspect_ratio * new_width * self.SYMBOL_RATIO)
        if new_height > self.max_height:
            new_height = self.max_height
            new_width = int(new_height / aspect_ratio / self.SYMBOL_RATIO)

        return new_width, new_height

    def pixels(self, pixels: np.ndarray, width: int, height: int) -> str:
        self.image_string = ""

        pixel_len = len(pixels[0])
        self.max_channel_values = 255 * pixel_len

        if pixel_len == 3:
            char = self.CHARACTERS[self.chars_count - 1]
            if self.type == self.TYPE_BGR:

                def map_char(pixel: BGRPixel):
                    b, g, r = pixel
                    return (self.RGB_FOREGROUND % (r, g, b)) + char
            else:

                def map_char(pixel: RGBPixel):
                    return (self.RGB_FOREGROUND % tuple(pixel)) + char
        elif pixel_len == 4:

            def map_char(pixel: RGBAPixel):
                r, g, b, alpha = pixel
                char = self.map_alpha_to_character(alpha)
                if alpha <= self.ALPHA_THRESHOLD:
                    return self.RESET + " "
                return (self.RGB_FOREGROUND % (r, g, b)) + char
        else:

            def map_char(pixel):
                return str(pixel)

        for i, pixel in enumerate(pixels):
            self.image_string += map_char(pixel)
            if (i + 1) % width == 0:
                self.image_string += "\n"

        self.image_string += self.RESET

        return self.image_string

    def rows(self, rows: np.ndarray) -> str:
        self.image_string = ""

        row = rows[0]
        pixel = row[0]
        pixel_len = len(pixel)
        self.max_channel_values = 255 * pixel_len

        if pixel_len == 3:
            char = self.CHARACTERS[self.chars_count - 1]
            if self.type == self.TYPE_BGR:

                def map_char(pixel: BGRPixel):
                    b, g, r = pixel
                    return (self.RGB_FOREGROUND % (r, g, b)) + char
            else:

                def map_char(pixel: RGBPixel):
                    return (self.RGB_FOREGROUND % tuple(pixel)) + char
        elif pixel_len == 4:

            def map_char(pixel: RGBAPixel):
                r, g, b, alpha = tuple(pixel)
                char = self.map_alpha_to_character(alpha)
                if alpha <= self.ALPHA_THRESHOLD:
                    return self.RESET + " "
                return (self.RGB_FOREGROUND % (r, g, b)) + char
        else:

            def map_char(pixel):
                return str(pixel)

        for row in rows:
            for pixel in row:
                self.image_string += map_char(pixel)
            self.image_string += "\n"

        self.image_string += self.RESET

        return self.image_string

    def get_pixel_intensity(self, pixel: RGBPixel) -> float:
        """
        Returns the pixel's intensity value as a float
        """
        return sum(pixel) / self.max_channel_values

    def map_intensity_to_character(self, intensity: float):
        """
        Restuns the character that corresponds to the given pixel intensity
        """
        return self.CHARACTERS[round(intensity * self.chars_count) - 1]

    def map_alpha_to_character(self, alpha: int):
        """
        Restuns the character that corresponds to the given pixel alpha channel
        """
        return self.CHARACTERS[round(alpha * self.chars_count / 255) - 1]
