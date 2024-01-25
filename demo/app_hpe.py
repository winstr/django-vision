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
    source = 'rtsp://192.168.1.101:554/profile2/media.smp'
    resize = (640, 480)
    interval = 3
    track_on = True

    try:
        estimator = PoseEstimator()
        skipflags = SkipFlags(interval=interval)
        cap = VideoCapture(source)
        preds = None

        for frame in cap:
            frame = cv2.resize(frame, resize)

            if not next(skipflags):
                preds = estimator.estimate(frame, track_on, verbose=False)
            plot_pose(frame, preds)

            jpeg = to_jpeg(frame)
            data = to_http_multipart(jpeg)
            yield data

    except:
        traceback.print_exc()

    cap.release()


@app.route('/video')
def video():
    return flask.Response(
        main(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
