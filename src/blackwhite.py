import numpy as np
import cv2


class BlackWhite:
    CHARACTERS = {
        0x0000: " ",
        0x1100: "▀",
        0x0011: "▄",
        0x1111: "█",
        0x1010: "▌",
        0x0101: "▐",
        0x0010: "▖",
        0x0001: "▗",
        0x1000: "▘",
        0x1011: "▙",
        0x1001: "▚",
        0x1110: "▛",
        0x1101: "▜",
        0x0100: "▝",
        0x0110: "▞",
        0x0111: "▟",
    }
    SYMBOL_RATIO = 0.42
    # MIDDLE_SHADE = 255 // 2
    MIDDLE_SHADE = 100

    def __init__(
        self,
        max_width: int = 80,
        max_height: int = 20,
        force_width: int | None = None,
        mirror: bool = False,
    ) -> None:
        self.max_width = max_width
        self.max_height = max_height
        self.force_width = force_width
        self.mirror = mirror

        self.CHAR_LUT = np.array(
            [self.CHARACTERS.get(i, " ") for i in range(0x1112)], dtype="<U1"
        )

        self.resize(max_width, max_height)

    def resize(self, width: int, height: int) -> tuple[int, int]:
        aspect_ratio = height / width
        self.cols = self.max_width if width > self.max_width else width
        if self.force_width is not None:
            self.cols = self.force_width
        new_width = self.cols * 2
        new_height = int(aspect_ratio * new_width * self.SYMBOL_RATIO)
        new_height = (new_height // 2) * 2

        if new_height > (self.max_height * 2):
            new_height = self.max_height * 2
            new_width = int(new_height / aspect_ratio / self.SYMBOL_RATIO)
            new_width = (new_width // 2) * 2
            self.cols = new_width // 2

        self.rows = new_height // 2
        self.buffer_size = self.rows * (self.cols + 1)
        self.frame = np.full(self.buffer_size, "\n", dtype="<U1")

        self.output_positions = (
            np.arange(self.rows)[:, None] * (self.cols + 1)  # +1 for newline
            + np.arange(self.cols)
        ).ravel()

        return new_width, new_height

    def cv2(self, frame: np.ndarray, frame_width: int, frame_height: int):
        resized_frame: np.ndarray = cv2.resize(
            frame,
            (frame_width, frame_height),
            interpolation=cv2.INTER_LINEAR,
        )
        gray_frame: np.ndarray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        if self.mirror:
            # gray_frame = cv2.flip(gray_frame, 1)
            gray_frame = gray_frame[:, ::-1]  # should be faster than cv2.flip

        self.pixels(gray_frame)

        # see np.ndarray(N) as np.ndarray(1) with long string without copying
        return self.frame.view(f"U{len(self.frame)}")[0]

    def pixels(self, pixels: np.ndarray) -> None:
        thresholded = pixels < self.MIDDLE_SHADE

        block_keys = (
            (thresholded[::2, ::2] << 12)  # 0x1000
            | (thresholded[::2, 1::2] << 8)  # 0x0100
            | (thresholded[1::2, ::2] << 4)  # 0x0010
            | thresholded[1::2, 1::2]  # 0x0001
        ).astype(np.uint16)

        valid_positions = self.output_positions[: block_keys.size]

        self.frame[self.output_positions] = self.CHAR_LUT[block_keys.ravel()]
