from PIL import Image


class Grayscale:
    CHARACTERS = (' ', '.', '°', '*', 'o', 'O', '#', '@')
    # SYMBOL_RATIO = 0.55
    SYMBOL_RATIO = 0.42

    def __init__(self, image: Image, max_width = 120, force_width = None) -> None:
        # self.CHARACTERS = tuple(' .:!/r(l1Z4H9W8$@')

        width, height = image.size
        aspect_ratio = height/width
        new_width = max_width if width > max_width else width
        if force_width != None:
            new_width = force_width
        new_height = aspect_ratio * new_width * self.SYMBOL_RATIO
        image = image.resize((new_width, int(new_height)))

        width, height = image.size

        # convert image to greyscale format
        image = image.convert('L')

        chars_count = len(self.CHARACTERS)

        # grayscale
        new_pixels = [self.CHARACTERS[round(pixel * chars_count / 255) - 1] for pixel in image.getdata()]
        self.ascii_string = ''.join(new_pixels)
        # split string of chars into multiple strings of length equal to new width and create a list
        new_pixels_count = len(self.ascii_string)
        ascii_image = [self.ascii_string[index:index + new_width]
                       for index in range(0, new_pixels_count, new_width)]
        self.ascii_string = "\n".join(ascii_image)

    def __call__(self) -> str:
        return self.ascii_string
