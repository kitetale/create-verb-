import cv2
import time
import os
from HandTracking import * 

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# folderPath = "FingerImages"
# myList = os.listdir(folderPath)
# print(myList)
# overlayList = []
# for imPath in myList:
#     image = cv2.imread(f'{folderPath}/{imPath}')
#     # print(f'{folderPath}/{imPath}')
#     overlayList.append(image)

# print(len(overlayList))
pTime = 0

detector = handDetector(detectionCon=0.75)

tipIds = [4, 8, 12, 16, 20]

while True:
    success, img = cap.read()
    img = cv2.flip(img,1)
    img = detector.findHands(img)

    length = 0
    if (detector.results.multi_hand_landmarks): length = len(detector.results.multi_hand_landmarks)

    cv2.rectangle(img, (20, 20), (200, 125), (255,255,255), cv2.FILLED)

    for handindex in range(length) :
        lmList = detector.findPosition(img, handNo=handindex, draw=False)
        print("hand #"+str(handindex) + " : ")
        #print(lmList)
        if len(lmList) != 0:
            fingers = []

            print(detector.results.multi_handedness[handindex].classification[0].label)
            # Thumb
            # note camera is flipped so follow the comment for correct orientation of hands
            if (detector.results.multi_handedness[handindex].classification[0].label == "Left"): #right hand
                if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else : #left hand
                if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # 4 Fingers
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            print(fingers)
            totalFingers = fingers.count(1)
            print(totalFingers)

            # h, w, c = overlayList[totalFingers - 1].shape
            # img[0:h, 0:w] = overlayList[totalFingers - 1]

            cv2.putText(img, str(totalFingers), (15+handindex*70, 100), cv2.FONT_HERSHEY_PLAIN,
                        5, (255, 0, 0), 10)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN,
                3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)