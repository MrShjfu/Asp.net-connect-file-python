# noinspection PyUnresolvedReferences
import sys
import cv2
# noinspection PyUnresolvedReferences
import numpy as np
# noinspection PyUnresolvedReferences
import imutils
# noinspection PyUnresolvedReferences
import PIL
# noinspection PyUnresolvedReferences
from exceptions import IOError
# noinspection PyUnresolvedReferences
from removeBlack import removeBlack
# noinspection PyUnresolvedReferences


#find keypoint and description with function Surf from Cv2
def extractIPAndSurf(img1, img2):
    # Initialize SURF
    surf = cv2.SIFT()
    # find the keypoint and description with sift
    #key1, key2 is keypoint of img1, img2
    # des1,des2 is description of img1,img2
    key1, des1 = surf.detectAndCompute(img1, None)
    key2, des2 = surf.detectAndCompute(img2, None)
    return key1, des1, key2,des2

#matching des1 and des2 with flann based matcher
def match(des1, des2):
    # Bruteforce matcher on the descriptors
    FLANN_INDEX_KDTREE = 0
    # initi parameter of flann
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # Make sure that the matches are good
    good_matchers = []
    # choose good point to matching
    for m1, m2 in matches:
        # Add to array only if it's a good match
        if m1.distance < 0.75 * m2.distance:
            good_matchers.append(m1)
    return good_matchers

#find homography
def homography(good_matchers, key1, key2):
    # Mimnum number of matches
    min_matches = 10
    if len(good_matchers) > min_matches:
        # src is matrix keypoint of imge1 and dst of image 2
        src = np.float32([key1[good_match.queryIdx].pt for good_match in good_matchers]).reshape(-1,1,2)
        dst = np.float32([key2[good_match.trainIdx].pt for good_match in good_matchers]).reshape(-1,1,2)
        # compute homography matrix by cv2.RANSAC,
        # M is homography matrix
        M, mask =cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
        return M
    else:
        print 'Not enough keypoint to matches'
        exit()

#create affine transfrom
def affineTransform(img1, img2,M):
    # Get width and height of input images
    w1, h1 = img1.shape[:2]
    w2, h2 = img2.shape[:2]

    # Get the canvas dimensions
    coor_img1 = np.array([[[0, 0]], [[0, w1]], [[h1, w1]], [[h1, 0]]], dtype="float32")
    coor_img2 = np.array([[[0, 0]], [[0, w2]], [[h2, w2]], [[h2, 0]]], dtype="float32")

    # Get relative perspective of second image from hommograpy
    coor_img2_new = cv2.perspectiveTransform(coor_img2, M)


    [x_min_coor_img2, y_min_coor_img2] = np.int32(coor_img2_new.min(axis=0).ravel())
    [x_max_coor_img2, y_max_coor_img2] = np.int32(coor_img2_new.max(axis=0).ravel())
    [x_min_coor_img1, y_min_coor_img1] = np.int32(coor_img1.min(axis=0).ravel())
    [x_max_coor_img1, y_max_coor_img1] = np.int32(coor_img1.max(axis=0).ravel())


    x_min = min(x_min_coor_img2, x_min_coor_img1)
    y_min = min(y_min_coor_img1, y_min_coor_img2)
    x_max = max(x_max_coor_img1, x_max_coor_img2)
    y_max = max(y_max_coor_img1, y_max_coor_img2)
    list = [x_min,x_max,y_min,y_max]
    # create affine transfrom,
    transform_array = np.array([[1, 0, -1 * x_min],
                                [0, 1, -1 * y_min],
                                [0, 0, 1]], dtype="float32")
    return transform_array,list


#matching image
def panoramaSample(img1, img2, M):
    # Get width and height of input images
    w1, h1 = img1.shape[:2]
    w2, h2 = img2.shape[:2]

    # Get the canvas dimensions
    coor_img1 = np.array([[[0, 0]], [[0, w1]], [[h1, w1]], [[h1, 0]]], dtype="float32")
    coor_img2 = np.array([[[0, 0]], [[0, w2]], [[h2, w2]], [[h2, 0]]], dtype="float32")

    # Get relative perspective of second image from hommograpy
    coor_img2_new = cv2.perspectiveTransform(coor_img2, M)

    # Resulting dimensions
    # function: Connect two matrices return one matric
    [x_min_coor_img2, y_min_coor_img2] = np.int32(coor_img2_new.min(axis=0).ravel())
    [x_max_coor_img2, y_max_coor_img2] = np.int32(coor_img2_new.max(axis=0).ravel())
    [x_min_coor_img1, y_min_coor_img1] = np.int32(coor_img1.min(axis=0).ravel())
    [x_max_coor_img1, y_max_coor_img1] = np.int32(coor_img1.max(axis=0).ravel())

    # Getting images together
    # Calculate dimensions of match points
    x_min = min(x_min_coor_img2,x_min_coor_img1)
    y_min = min(y_min_coor_img1,y_min_coor_img2)
    x_max = max(x_max_coor_img1,x_max_coor_img2)
    y_max = max(y_max_coor_img1, y_max_coor_img2)
    # create affine transfrom,
    transform_array = np.array([[1, 0, -1 * x_min],
                                [0, 1, -1 * y_min],
                                [0, 0, 1]], dtype="float32")

    # create matrix of tranform affind and homography
    homography = np.dot(transform_array, M)
    # get size of new image
    height =y_max-y_min
    width =x_max-x_min
    size = (width,height)
    # Warp images to get the resulting image
    result_img = cv2.warpPerspective(img2, homography, size)
    result_img[-y_min:w1 -y_min, -x_min:h1 -x_min] = img1
    # Return the result
    return result_img

#function call extract Ip,surt and find homography
def findMatch_homography(img1,img2):
    #return match and keypoint of img1,2
    k1,d1, k2,d2 = extractIPAndSurf(img1,img2)
    good_point=match(d1,d2)
    try:
        M = homography(good_point,k1,k2)
        return M
    except:
        print "Not enough keypoint to find homography"



# Main function definition
def main(listOfImages):
    print listOfImages
    # read image and resize
    for image in range(1, len(listOfImages), 1):
        listOfImages[image] = cv2.imread(listOfImages[image])
        w, h = listOfImages[image].shape[:2]
        if w > 400:
            listOfImages[image] = imutils.resize(listOfImages[image], width=400)
    # if only input 2 images

    M = findMatch_homography(listOfImages[2], listOfImages[1])
    result_image = panoramaSample(listOfImages[1], listOfImages[2], M)
    print '2'
    # else if
    if len(listOfImages) >= 2:
        for image in range(2, len(listOfImages), 1):
                print image
                M = findMatch_homography(result_image, listOfImages[image])
                result_image = panoramaSample(listOfImages[image], result_image, M)
    # file will save D:/result.jpg, replay when running
    # call function remove Background black, but dont crop all background
    cv2.imwrite(listOfImages[0], result_image)
    cv2.waitKey()

if __name__ == '__main__':
    main(sys.argv[1:])