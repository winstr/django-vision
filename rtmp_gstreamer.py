import argparse
import traceback

import cv2
import gi
#import numpy as np
gi.require_version('Gst', '1.0')
from gi.repository import Gst


Gst.init(None)
PIPELINE_STR = (
    "appsrc name=source is-live=true block=true format=GST_FORMAT_TIME "
    "caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! "
    "videoconvert ! "
    "x264enc speed-preset=ultrafast tune=zerolatency ! "
    "flvmux streamable=true name=mux ! "
    "rtmpsink location='rtmp://192.168.1.200:1935/live/stream live=1'")
PIPELINE = Gst.parse_launch(PIPELINE_STR)
APPSRC = PIPELINE.get_by_name('source')


def push_frame(arr):
    data = arr.tobytes()
    buffer = Gst.Buffer.new_allocate(None, len(data), None)
    buffer.fill(0, data)
    APPSRC.emit('push-buffer', buffer)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str)
    args = parser.parse_args()
    source = args.source

    cap = cv2.VideoCapture(source)
    assert cap.isOpened(), 'failed to open the video source.'

    try:
        print(f'Starting RTMP stream to {PIPELINE_STR}')
        PIPELINE.set_state(Gst.State.PLAYING)

        while True:
            is_captured, frame = cap.read()
            assert is_captured, 'failed to capture the next frame.'

            frame = cv2.resize(frame, (640, 480))
            push_frame(frame)

    except Exception as e:
        print(f'An error occurred: {e}')
        traceback.print_exc()

    cap.release()
    PIPELINE.set_state(Gst.State.NULL)
    print('RTMP stream stopped')
