import sys
import traceback
from pathlib import Path

import cv2
import flask

sys.path.append(str(Path(__file__).parents[1]))
from observer.utils.video import SkipFlags, VideoCapture
from observer.engine.yolov8.pose import PoseEstimator, plot_pose


app = flask.Flask(__name__)


def to_jpeg(frame):
    is_encoded, jpeg = cv2.imencode('.jpeg', frame)
    if not is_encoded:
        msg = 'Failed to encode the frame.'
        raise RuntimeError(msg)
    return jpeg.tobytes()


def to_http_multipart(jpeg: bytes):
    return (
        b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n'
        + jpeg +
        b'\r\n')


def main():
    video_source = 'rtsp://192.168.1.101:554/profile2/media.smp'
    target_size = (640, 480)
    skip_interval = 3

    try:
        estimator = PoseEstimator()
        skip_flags = SkipFlags(skip_interval)
        preds = None

        cap = VideoCapture(video_source)
        while True:
            frame = next(cap)
            frame = cv2.resize(frame, target_size)

            skip_on = next(skip_flags)
            if not skip_on:
                preds = estimator.estimate(frame, verbose=False)
            plot_pose(frame, preds)

            jpeg = to_jpeg(frame)
            data = to_http_multipart(jpeg)
            yield data

    except:
        traceback.print_exc()

    finally:
        cap.release()


@app.route('/video')
def video():
    return flask.Response(
        main(),
        mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
