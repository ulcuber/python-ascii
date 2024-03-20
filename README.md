# python image-to-text converter

-   Uses PIL
-   Adaptive image ratio and width
-   Converts image to grayscale, every grayscale pixel to symbol
-   Converts image to grayscale, every 4 pixels to symbol (black and white only)
-   Uses image RGB to print RGB escape codes `\033[38;2;`

## Run

```bash
. bin/activate
python src/image-to-ascii.py --help
```

# python video-to-text player

-   Uses OpenCV
-   Adaptive video ratio and width

## Run

```bash
. bin/activate
python src/video-to-ascii.py --help
```

## Debug

```bash
export OPENCV_VIDEOIO_DEBUG=1
export OPENCV_LOG_LEVEL=debug
```

# Install

```bash
make venv
. ./bin/activate
make install
```
