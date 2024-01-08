import argparse
import traceback

import cv2
import flask

from lib.pose import Pose


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

    pose = Pose()
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
