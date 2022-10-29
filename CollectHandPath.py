# combination of CountFinger.py and generateButterfly.py
# @kitetale 
# 10.29.2022 ExCap Project 2 OpenCV handtracking file

import time
import os
import sys
from datetime import datetime

from HandTracking import * 

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

elapsed = 0
startTime = datetime.now()
secondsElapsed = 0
halfSeconds = 0
newTime = False

pTime = 0

detector = handDetector(detectionCon=0.75)

tipIds = [4, 8, 12, 16, 20]

captureNew = True

handPath = []
collectPath = True

ready = False

totalCount = 0

pause = 0
pausefor = 5.0
updated = False

def prepareScript (handPath):
    script1 = os.getcwd() + "/Script1.py"
    fd1 = open(script1,'w')
    fd1.write("def make (generateButterfly): \n \t generateButterfly("+str(handPath)+")")
    print("updated script1! ")
    fd1.close()

    
    


############################## opencv loop ####################################
while True:
    #Update Second / halfsecond increment
    elapsed = (datetime.now() - startTime).total_seconds()
    if (elapsed//1 != secondsElapsed): 
        secondsElapsed = elapsed//1
        # print(secondsElapsed)
    if (halfSeconds!=(((elapsed*10)//1)/10) and ((elapsed*10)//1)%5 == 0):
        halfSeconds = ((elapsed*10)//1)/10
        print(halfSeconds)
        newTime = True

    success, img = cap.read()
    img = cv2.flip(img,1)

    # check if butterfly is being generated
    if (not collectPath and not ready):
        if ((halfSeconds-pause) >= pausefor): #waited enough
            updated = True
        if updated :
            collectPath = True
            updated = False
        else :
            #wait more
            cv2.imshow("Image", img)
            cv2.waitKey(1)
            
    else :
        img = detector.findHands(img)

        length = 0
        if (detector.results.multi_hand_landmarks): length = len(detector.results.multi_hand_landmarks)

        cv2.rectangle(img, (20, 20), (200, 125), (255,255,255), cv2.FILLED)

        for handindex in range(length) :
            lmList = detector.findPosition(img, handNo=handindex, draw=False)

            if len(lmList) != 0:
                fingers = []

                # rotation of hand (0/180 or 90/-90)
                x = 1
                y = 2
                distx = abs(lmList[2][x] - lmList[17][x])
                disty = abs(lmList[2][y] - lmList[17][y])
                if (distx < disty):
                    x = 2
                    y = 1

                # horizontal orientation of hand 
                rightHand = False
                if lmList[17][x] > lmList[2][x]: rightHand = True

                # Thumb
                if (rightHand): #right hand
                    if lmList[tipIds[0]][x] < lmList[tipIds[0] - 1][x]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                else : #left hand
                    if lmList[tipIds[0]][x] > lmList[tipIds[0] - 1][x]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                
                # vertical orientation of hand
                updir = True
                if lmList[0][y] < lmList[9][y]: updir = False

                # 4 Fingers
                for id in range(1, 5):
                    if (updir):
                        if lmList[tipIds[id]][y] < lmList[tipIds[id] - 2][y]:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    else:
                        if lmList[tipIds[id]][y] > lmList[tipIds[id] - 2][y]:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                totalFingers = fingers.count(1)

                # get location of thumb root into hand path array
                if collectPath:
                    if (len(handPath) > 10): handPath = handPath[1:]
                    if (lmList != [] and halfSeconds == ((elapsed*10)//1)/10 and newTime):
                        handPath.append((lmList[2][x]/10,lmList[2][y]/10))
                        print(handPath)
                        newTime = False

                # if 10 points collected, ready for generating butterfly!
                if ((len(handPath) >= 10) and (collectPath) and (totalFingers==0)): 
                    # preparing to generate butterfly
                    pause = halfSeconds
                    collectPath = False
                    ready = True
                # once ready, open hand to generate
                if (ready and totalFingers==5):
                    totalCount += 1
                    prepareScript(handPath)
                    pause = halfSeconds
                    ready = False
                    updated = False
                    handPath = []

                # h, w, c = overlayList[totalFingers - 1].shape
                # img[0:h, 0:w] = overlayList[totalFingers - 1]

                cv2.putText(img, str(totalFingers), (15+handindex*70, 100), cv2.FONT_HERSHEY_PLAIN,
                            5, (255, 0, 0), 10)

        #Update FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 0, 0), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)

