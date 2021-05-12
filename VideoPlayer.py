#!/usr/bin/env python3

import cv2
import threading
import os
import queue
import base64

mutex=threading.Lock()

class ThreadQueue():
    def __init__(self):
        self.semaphore=threading.Semaphore(10)
        self.queue = queue.Queue()
    def put(self,frame):
        self.semaphore.acquire()
        mutex.acquire()
        self.queue.put(frame)
        mutex.release()

    def get(self):
        self.semaphore.release()
        mutex.acquire()
        frame=self.queue.get()
        mutex.release()
        return frame

    def isEmpty(self):
        mutex.acquire()
        isEmpty=self.queue.empty()
        mutex.release()
        return isEmpty

FirstQueue=ThreadQueue()

SecondQueue=ThreadQueue()

filename='clip.mp4'

c=cv2.VideoCapture(filename)

total=int(c.get(cv2.CAP_PROP_FRAME_COUNT))-1

def ExtractFrames(filename):
    count=0
    vidcap = cv2.VideoCapture(filename)
    success,image = vidcap.read()
    os.write(1,(f'Reading frame {count}{success}\n').encode())
    while success:
        success,jpgImage = cv2.imencode('.jpg',image)
        FirstQueue.put(image)
        count+=1
        success,image=vidcap.read()
        os.write(1,(f'reading frame {count}\n').encode())
    os.write(1,(f'Extracted all frames\n').encode())

def ConvertToGrayscale():
    count=0
    while True:
        if FirstQueue.isEmpty():
            continue
        getting=FirstQueue.get()
        if count==total:
            os.write(1,(f'Converting last frame {count}\n').encode())
            break
        grayscaleFrame = cv2.cvtColor(getting,cv2.COLOR_BGR2GRAY)
        SecondQueue.put(grayscaleFrame)
        os.write(1,(f'Converting frame{count}\n').encode())
        count+=1

def DisplayFrames():
    count=0
    while True:
        if count==total:
            os.write(1,f'Displaying last frame {count}\n'.encode())
            break
        if SecondQueue.isEmpty():
            continue
        frame=SecondQueue.get()
        os.write(1,f'Displaying Frame {count}\n'.encode())
        cv2.imshow('Video',frame)
        if cv2.waitKey(42)and 0xFF == ord("q"):
            break
        count+=1
    os.write(1,f'Finished displaying all frames'.encode())
    cv2.destroyAllWindows()
ExtractThread=threading.Thread(target=ExtractFrames,args=(filename,))
ConvertThread=threading.Thread(target=ConvertToGrayscale)
DisplayThread=threading.Thread(target=DisplayFrames)
ExtractThread.start()
ConvertThread.start()
DisplayThread.start()
