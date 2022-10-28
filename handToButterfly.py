# combination of CountFinger.py and generateButterfly.py
# @kitetale 
# 10.28.2022 ExCap Project 2 Blender python

import bpy
import time
import os
import sys
from datetime import datetime
# ################# Import opencv and mediapipe for handtracking
# import subprocess
# python_folder = os.path.join(sys.prefix, 'bin', 'python')
# py_lib = os.path.join(sys.prefix, 'lib', 'site-packages', "-m", 'pip')

# #subprocess.call([python_folder,py_lib,"install","opencv_python"])
# subprocess.call([python_folder,py_lib,"install","mediapipe"])
################ Import HandTracking.py
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

from HandTracking import * 
#################

# [input] handPath : list of xyz coord of butterfly path
# [input] count : number of total butterflies generated so far
def generateButterfly(handPath, count):
    # Cache shortcuts to start and end of scene.
    scene = bpy.context.scene
    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end
    frame_mid = frame_start + ((frame_end - frame_start)//2)

    # Create cube.
    # ops.mesh.primitive_cube_add(radius=1.0, location=(0.0, 0.0, 0.0))
    # cube = context.active_object

    # number of objects in scene: use to offset location later
    butterflyNum = len(bpy.context.collection.objects)
    offset = 60

    # manage maximum number of butterflies on screen
    maxNum = 5
    if (butterflyNum > maxNum) : 
        removingNum =  int(bpy.context.collection.objects[1].name[10:13])
        bpy.data.objects.remove( bpy.data.objects[1],do_unlink=True)
        butterflyNum = removingNum % (maxNum)

    #offset info
    offsetPos = offset * butterflyNum
    col = 5
    widthLimit = offset * col


    # Create Butterfly
    butterfly = bpy.data.objects['Butterfly'] # mesh data input
    creation = bpy.data.objects.new('Butterfly',butterfly.data) #instance

    # add instance to scene
    bpy.context.collection.objects.link(creation)
    #bpy.context.collection.update() #add to the scene

    #copy modifiers
    butterfly.select_set(True, view_layer=scene.view_layers[0])
    bpy.context.view_layer.objects.active = butterfly
    creation.select_set(True, view_layer=scene.view_layers[0])
    bpy.ops.object.make_links_data(type='MODIFIERS')
    bpy.ops.object.select_all(action='DESELECT')

    #deleting instance:
    # bpy.data.objects.remove( bpy.data.objects['Butterfly.000'],do_unlink=True)

    #location list from hand track program
    #handPath = [(33.2, 50.0, 0), (55.5, 39.5, 0), (51.2, 25.2, 0), (30.3, 18.8, 0), (24.5, 19.2, 0), (38.4, 18.9, 0), (46.1, 25.9, 0), (41.8, 46.8, 0), (56.0, 35.7, 0), (53.6, 21.4, 0), (48.8, 24.8, 0)]

    # Loop through locations list.
    pathLen = len(handPath)
    i_to_percent = 1.0 / (pathLen - 1)
    i_range = range(0, pathLen, 1)

    # follow path in order
    for i in i_range:
        # Convert place in locations list to appropriate frame.
        i_percent = i * i_to_percent
        key_frame = int(frame_start * (1.0 - i_percent) + frame_mid * i_percent)
        scene.frame_set(key_frame)

        # Update location for that frame. [TODO]
        offsetY = 0
        offsetX = 0
        creation.location = (handPath[i][0]+offsetX,handPath[i][1]+offsetY,0)
        creation.keyframe_insert(data_path='location')

    # reverse the path to allow loop to happen
    for i in i_range:
        i_percent = i * i_to_percent
        key_frame = int(frame_mid * (1.0 - i_percent) + frame_end * i_percent)
        scene.frame_set(key_frame)

        # Update location for that frame. [TODO]
        offsetY = 0
        offsetX = 0
        creation.location = (handPath[pathLen-1-i][0]+offsetX,handPath[pathLen-1-i][1]+offsetY,0)
        creation.keyframe_insert(data_path='location')

    # Cache shortcut to f-curves.
    fcurves = creation.animation_data.action.fcurves
    for fcurve in fcurves:
        for key_frame in fcurve.keyframe_points:

            # Set interpolation and easing type.
            key_frame.interpolation = 'BEZIER'
            key_frame.easing = 'AUTO'

            # Options: ['FREE', 'VECTOR', 'ALIGNED', 'AUTO', 'AUTO_CLAMPED']
            key_frame.handle_left_type = 'FREE'
            key_frame.handle_right_type = 'FREE'


    # Return to starting frame.
    scene.frame_set(frame_start)

############################# Blender Python #################################


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

handPath = []
collectPath = True

ready = False

totalCount = 0


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
                collectPath = False
                ready = True
            # once ready, open hand to generate
            if (ready and totalFingers==5):
                totalCount += 1
                generateButterfly(handPath, totalCount)
                collectPath = True
                ready = False
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


############################# Blender Python #################################
