import argparse
import traceback

import cv2
import flask

from lib.yolo import PoseEstimator


app = flask.Flask(__name__)


SOURCE = None  # e.g. 'rtsp://...'
RESOLUTION = None  # e.g. (640, 480)


def generate_jpeg():

    def capture():
        is_captured, frame = cap.read()
        assert is_captured, 'failed to capture the next frame.'
        return frame

    def preproc(frame):
        frame = cv2.resize(frame, RESOLUTION)
        return frame

    def postproc(frame):
        is_encoded, jpeg = cv2.imencode('.jpg', frame)
        assert is_encoded, 'failed to encode the frame.'
        jpeg = jpeg.tobytes()
        return jpeg

    cap = cv2.VideoCapture(SOURCE)
    assert cap.isOpened(), 'failed to open the video source.'

    pose = PoseEstimator()
    results = None

    frame_skip = 3
    frame_count = 0
    try:
        while True:
            frame = capture()
            frame = preproc(frame)
            if frame_count == 0:
                results = pose.estimate(frame, enable_tracking=True, verbose=False)
            frame = pose.visualize(results)
            if frame_count < frame_skip - 1:
                frame_count += 1
            else:
                frame_count = 0
            jpeg = postproc(frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
    except:
        traceback.print_exc()

    cap.release()
    cv2.destroyAllWindows()


@app.route('/video')
def video():
    return flask.Response(
        generate_jpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str)
    args = parser.parse_args()

    SOURCE = args.source
    RESOLUTION = (640, 480)

    app.run(host='0.0.0.0', port=8080)

"""
TMP

import time
import logging
import argparse
import traceback

import cv2
import flask
import numpy as np


class App():

    @staticmethod
    def _convert_to_jpeg(frame: np.ndarray):
        encoded, jpeg = cv2.imencode('.jpg', frame)
        assert encoded, 'Failed to encode the array.'
        return jpeg.tobytes()

    def __init__(self, src, skip=0, prep_fn=None, pred_fn=None, post_fn=None):
        self._src = src
        self._cap = None
        self._fps = None
        self._skip = skip
        self._prep_fn = prep_fn
        self._pred_fn = pred_fn
        self._post_fn = post_fn
        self._build()

    def _build(self):
        self._cap = cv2.VideoCapture(self._src)
        assert self._cap.isOpened(), 'Failed to read the video source.'
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)

    def _read_frame(self) -> np.ndarray:
        captured, frame = self._cap.read()
        assert captured, 'Failed to read the next frame.'
        return frame

    def _preprocess(self, frame) -> np.ndarray:
        return self._prep_fn(frame) if self._prep_fn else frame

    def _predict(self, frame) -> np.ndarray:
        return self._pred_fn(frame) if self._pred_fn else frame

    def _postprocess(self, frame, preds) -> np.ndarray:
        return self._post_fn(frame, preds) if self._post_fn else frame

    def _play_video(self):
        try:
            count = 0
            preds = None
            delay = 1.0 / self._fps
            while True:
                start_time = time.time()

                frame = self._read_frame()
                frame = self._preprocess(frame)

                if count == 0:
                    preds = self._predict(frame)
                count = count + 1 if count < self._skip else 0

                frame = self._postprocess(frame, preds)
                frame = self._convert_to_jpeg(frame)

                elapsed_time = time.time() - start_time
                delayed_time = delay - elapsed_time
                if delayed_time:
                    time.sleep(delayed_time)

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            traceback.print_exc()

        self._cap.release()


def play_video():
    cap = cv2.VideoCapture()
    assert cap.isOpened(), 'Failed to open the video source.'


@app.route('/video')
def video():
    return flask.Response(
        response=play_video,
        mimetype='multipart/x-mixed-replace; boundary=frame',
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_source', type=str)

"""