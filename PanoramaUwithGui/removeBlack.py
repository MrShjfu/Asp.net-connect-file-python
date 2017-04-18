# noinspection PyUnresolvedReferences
import cv2
# noinspection PyUnresolvedReferences
import numpy as np
# noinspection PyUnresolvedReferences
from PIL import Image
def removeBlack(img):
    tmp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    b, g, r = cv2.split(img)
    rgba = [b, g, r, alpha]
    dst = cv2.merge(rgba, 4)
    return dst