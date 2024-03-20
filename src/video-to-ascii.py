import argparse
import shutil
import sys
import time
from blackwhite import BlackWhite
import cv2
import numpy as np

from grayscale import Grayscale
from rgba import RGBA

def get_args():
    size = shutil.get_terminal_size((80, 20))

    parser = argparse.ArgumentParser(description='Image to ASCII converter')

    parser.add_argument('--max_width', type=int, default=size.columns,
                    help='Maximum width to resize bigger image to in symbols. Default to COLUMNS')
    parser.add_argument('--force_width', type=int,
                    help='Width to resize image to in symbols even if image is smaller. Default to image width or COLUMNS')
    parser.add_argument('--max_height', type=int, default=size.lines,
                    help='Maximum height to resize bigger image to in symbols. Default to LINES')
    parser.add_argument('--video', type=str, default=0,
                    help='Path to video. Default to webcam')
    parser.add_argument('--converter', type=str, default='grayscale',
                        choices=['grayscale', 'rgba', '4blackwhite'],
                        help='Converter to use. One of: grayscale (default), rgba, 4blackwhite (x4 resolution)')

    return parser.parse_args()

def main():
    args = get_args()

    video = args.video
    force_width = args.force_width
    max_width = args.max_width
    max_height = args.max_height
    converter = args.converter

    if converter == 'grayscale':
        driver = Grayscale(max_width=max_width, max_height=max_height, force_width=force_width)
    elif converter == '4blackwhite':
        driver = BlackWhite(max_width=max_width, max_height=max_height, force_width=force_width)
    elif converter == 'rgba':
        driver = RGBA(max_width=max_width, max_height=max_height, force_width=force_width)
    else:
        raise Exception('Unsupported Converter')

    cap = cv2.VideoCapture(video)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video == 0:
        def drop_frames(count: float):
            pass
    else:
        def drop_frames(count: float):
            current = cap.get(cv2.CAP_PROP_POS_FRAMES)
            cap.set(cv2.CAP_PROP_POS_FRAMES, current + count)

    if not cap.isOpened():
        print('Cannot open capture')
        exit(1)

    if video == 0:
        driver.mirror = True

    CUP = "\033[%d;%dH"

    video_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width, height = driver.resize(int(width), int(height))

    nano = 1_000_000_000
    per_frame = int(nano / video_fps)

    elapsed = 0
    elapsed_real = 0
    elapsed_total = 0
    elapsed_frames = -1
    total_frames = -1
    real_frames = 0
    dropped_frames = 0
    fps = 0
    info = None
    ret = None
    frame = None

    start = time.time_ns()
    prev = start
    while cap.isOpened():
        now = time.time_ns()
        elapsed = now - prev
        prev = now
        elapsed_total += elapsed

        elapsed_frames += 1
        if elapsed_total >= nano:
            elapsed_total -= nano
            fps = elapsed_frames
            elapsed_frames = 0
            info = f"FPS: {fps}/{video_fps}, ({elapsed}/{per_frame})ns, frames: {total_frames}/{video_frames} -{dropped_frames}"

        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        text = driver.cv2(frame, width, height)

        sys.stdout.write(CUP % (0, 0))
        sys.stdout.write(text)

        if info:
            sys.stdout.write(CUP % (0, 0))
            sys.stdout.write(info)

        sys.stdout.flush()

        now = time.time_ns()
        total_frames += 1
        elapsed_real = now - start
        remainder = (total_frames * per_frame - elapsed_real) / nano
        if remainder > 0:
            time.sleep(remainder)
        elif remainder < 0:
            elapsed_real = time.time_ns() - start
            real_frames = round(elapsed_real / per_frame)
            frame_lag = real_frames - total_frames
            if frame_lag > 0:
                drop_frames(frame_lag)
                total_frames = real_frames
                dropped_frames += frame_lag

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
