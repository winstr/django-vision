import time
import traceback

import cv2
import flask

from observer.utils.plotting import plot_text
from observer.utils.video import SkipFlags, VideoCapture
from observer.engine.yolov8.pose import PoseEstimator, plot_pose


app = flask.Flask(__name__)


class Timer():

    @staticmethod
    def _to_strftime(elapsed_time):
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'

    def __init__(self):
        self.init_time = time.time()
    
    def _elapsed(self):
        return time.time() - self.init_time

    def strftime(self):
        return self._to_strftime(self._elapsed())


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
        timer = Timer()
        estimator = PoseEstimator()
        skipflags = SkipFlags(interval=interval)
        cap = VideoCapture(source)
        preds = None

        for frame in cap:
            frame = cv2.resize(frame, resize)

            if not next(skipflags):
                preds = estimator.estimate(frame, track_on, verbose=False)
            plot_pose(frame, preds)

            strftime = timer.strftime()
            plot_text(frame, strftime, (10, 10), (255, 255, 255))

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
