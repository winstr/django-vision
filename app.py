import argparse
import traceback

import cv2
import flask

from observer.utils.video import VideoFrameSkipper, VideoCapture
from observer.engine.yolov8.pose import DefaultPose, PoseEstimator


app = flask.Flask(__name__)
source: str = None


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


def generate_jpeg():
    pose_estimator = PoseEstimator()
    vframe_skipper = VideoFrameSkipper(skip_interval=3)

    preds = None
    with VideoCapture(source) as cap:
        try:
            for frame in cap:
                frame = cv2.resize(frame, (640, 480))

                skip = next(vframe_skipper)
                if not skip:
                    preds = pose_estimator.estimate(
                        frame, enable_tracking=True,  verbose=False)

                DefaultPose.plot(frame, preds, enable_tracking=True)
                jpeg = to_jpeg(frame)
                data = to_http_multipart(jpeg)
                yield data
        except:
            traceback.print_exc()


@app.route('/video')
def video():
    return flask.Response(
        generate_jpeg(),
        mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str)

    args = parser.parse_args()
    source = args.source

    app.run(host='0.0.0.0', port=8080)
