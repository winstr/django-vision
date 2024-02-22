import json
import base64
import traceback

import cv2
import requests
import numpy as np


url = 'http://192.168.1.12:8000/'
response = requests.get(url, stream=True)

try:
	for line in response.iter_lines():
		if not line:
			continue

		data = json.loads(line.decode("utf-8"))
		frame_b64 = base64.b64decode(data["frame"])
		frame = np.frombuffer(frame_b64, dtype=np.uint8).copy()
		frame = frame.reshape((360, 640, 3))
		names = data["names"]
		boxes = data["boxes"]

		if boxes:
			boxes = np.array(boxes, dtype=float)
			xyxys = boxes[:, :4].astype(int)
			for xyxy in xyxys:
				pt1 = tuple(xyxy[:2])
				pt2 = tuple(xyxy[2:])
				cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 1)

		cv2.imshow("frame", frame)
		if cv2.waitKey(1) == ord('q'):
			break

except:
	traceback.print_exc()

finally:
	cv2.destroyAllWindows()
