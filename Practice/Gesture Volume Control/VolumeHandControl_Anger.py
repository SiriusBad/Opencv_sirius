import cv2
import time
import numpy as np
import HandModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(1)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img, draw=True)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x0, y0 = lmList[0][1], lmList[0][2]
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x0, y0), (0, 255, 255), 3)
        cv2.line(img, (x0, y0), (x2, y2), (0, 255, 255), 3)
        cv2.line(img, (x1, y1), (x2, y2), (238, 104, 123), 3)

        if (x1-x0) != 0 and (x2-x0) != 0:
            gradient1 = round(math.degrees(math.atan(abs(y1 - y0) / abs(x1 - x0))), 2)
            gradient2 = round(math.degrees(math.atan(abs(y2 - y0) / abs(x2 - x0))), 2)
            gradient = abs(gradient1 - gradient2)

        # print(gradient)

        # Hand range 50 - 300
        # Volume Range -65 - 0

        vol = np.interp(gradient, [4, 48], [minVol, maxVol])
        volBar = np.interp(gradient, [4, 48], [400, 150])
        volPer = np.interp(gradient, [4, 48], [0, 100])
        # print(int(gradient), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if gradient < 4:
            cv2.line(img, (x1, y1), (x0, y0), (0, 255, 0), 3)
            cv2.line(img, (x0, y0), (x2, y2), (0, 255, 0), 3)

    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    cv2.imshow("Img", img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
cv2.destroyAllWindows()