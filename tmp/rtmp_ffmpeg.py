import json
import time
import traceback
import subprocess
from typing import Dict

import cv2

from lib.pose import Pose


def main(args: Dict):
    cap = cv2.VideoCapture(args['rtsp_source_url'])
    assert cap.isOpened(), f'failed to open the video source.'

    res = (args['dst_video_resolution']['width'],
           args['dst_video_resolution']['height'])
    #fps = cap.get(cv2.CAP_PROP_FPS)
    fps = args['dst_video_fps']
    command = [
        'ffmpeg', '-y',
        '-use_wallclock_as_timestamps', '1',
        '-f', args['src_video_format'],
        '-vcodec', args['src_video_codec'],
        '-pix_fmt', args['src_video_pixel_format'],
        '-s', f'{res[0]}x{res[1]}',
        '-r', f'{fps}',
        '-i', '-',
        '-c:v', args['dst_video_codec'],
        '-pix_fmt', args['dst_video_pixel_format'],
        '-preset', args['encoding_speed'],
        '-vsync', '1',
        '-f', args['dst_video_format'],
        args['rtmp_server_url']]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)

    pose = Pose()
    results = None

    frame_skip = 3
    frame_count = 0
    try:
        interval_time = 1. / fps
        failure_count = 0
        while True:
            start_time = time.time()
            is_captured, frame = cap.read()
            if not is_captured:
                if failure_count >= 10:
                    assert False, 'failed to capture frame.'
                failure_count += 1
                continue
            frame = cv2.resize(frame, dsize=res)

            if frame_count == 0:
                results = pose.track(frame)
            frame = pose.plot(results, frame)
            if frame_count < frame_skip - 1:
                frame_count += 1
            else:
                frame_count = 0

            proc.stdin.write(frame.tobytes())

            elapsed_time = time.time() - start_time
            delayed_time = interval_time - elapsed_time
            if delayed_time > 0:
                time.sleep(delayed_time)
    except:
        traceback.print_exc()

    cap.release()
    proc.stdin.close()
    proc.wait()


if __name__ == '__main__':
    with open('config/ffmpeg_.json', 'r') as f:
        args = json.load(f)
    main(args)