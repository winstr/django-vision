import sys
import time
import traceback
from pathlib import Path

import cv2
import flask

sys.path.append(str(Path(__file__).parents[1]))
from observer.utils.color import Colors
from observer.utils.video import SkipFlags, VideoCapture
from observer.utils.plotting import plot_text
from observer.engine.yolov8.pose import PoseEstimator, _plot_kpts
from observer.engine.yolov8.pose import DEFAULT_CNMAP


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


class Timer():

    def __init__(self):
        self.start_time = time.time()

    def get_elapsed_time(self) -> str:
        elapsed_time = time.time() - self.start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        elapsed_time_str = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'
        return elapsed_time_str


def main():
    source = 'rtsp://192.168.1.101:554/profile2/media.smp'
    resize = (640, 480)
    interval = 3
    track_on = True
    shade = 300

    try:
        estimator = PoseEstimator()
        skipflags = SkipFlags(interval=interval)
        cap = VideoCapture(source)
        prev_box_ids = set()
        timers = {}

        colors = [color[shade] for color in Colors.all_colors]
        colors = [Colors.to_bgr(color) for color in colors]

        preds = None
        for frame in cap:
            frame = cv2.resize(frame, resize)

            if not next(skipflags):
                preds = estimator.estimate(frame, track_on, verbose=False)
                current_box_ids = set(preds[0].boxes.data.cpu().numpy()[:, 4].astype(int))

                dis_box_ids = prev_box_ids - current_box_ids
                for box_id in dis_box_ids:
                    del timers[box_id]
                
                new_box_ids = current_box_ids - prev_box_ids
                for box_id in new_box_ids:
                    timers[box_id] = Timer()

                prev_box_ids = current_box_ids

            if not preds is None:
                results = preds[0]
                boxes = results.boxes.data.cpu().numpy()
                kptss = results.keypoints.data.cpu().numpy()

                #for i, box in enumerate(boxes):
                for i, (box, kpts) in enumerate(zip(boxes, kptss)):
                    color = colors[i % len(colors)]
                    xyxy = tuple(box[:4].astype(int))
                    pt1, pt2 = xyxy[:2], xyxy[2:]
                    cv2.rectangle(frame, pt1, pt2, color, thickness=1)

                    _plot_kpts(frame, kpts, color, DEFAULT_CNMAP)

                    box_id = int(box[4])
                    box_conf = f'{(box[5]*100):.2f}%'
                    box_time = timers[box_id].get_elapsed_time()
                    plot_text(frame, f'Person, {box_conf}, {box_time}', pt1,
                              color=(0, 0, 0), bgcolor=color)

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
