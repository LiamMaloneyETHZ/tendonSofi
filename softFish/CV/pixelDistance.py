import cv2
import numpy as np
import pandas as pd


#goal of this code is to take a known value of height at the distance the fish is being measured, calibrate the camera to that distance
#then, determine the real-life distance given a pixel distance for a known height
points = []

"""
Camera matrix and distortion coefficients from rectangular calibration
# Camera matrix
mtx = np.array([
    [850.46282868, 0.0, 926.47015089],
    [0.0, 850.34124243, 546.3733339],
    [0.0, 0.0, 1.0]
])

# Distortion coefficients
dist = np.array([
    -3.20324366e-01,
     1.46621572e-01,
    -2.06803818e-03,
    -2.81291640e-04,
    -6.95534360e-02
])
"""
#Calibration values from the assymetric calibration set
# Camera matrix
mtx = np.array([
    [6854.02255, 0.0, 953.349510],
    [0.0, 6329.72942, 534.921515],
    [0.0, 0.0, 1.0]
])

# Distortion coefficients
dist = np.array([
    1.93965100e+01,
    1.03302061e+03,
    6.03419410e-01,
   -6.17968976e-02,
   -1.74216458e-01
])

#undistorts fish-eye lens
def undistort(mtx, dist, img):
    img = img
    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

    """
    # undistort
    mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
    dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
 
    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    cv.imwrite('calibresult_2.png', dst)
    """


    # undistort
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    return(dst)

#registers click
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(param, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('Image', param)

# Load an image or video frame
#this is just a straight read line
img = cv2.imread(r"C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\Dynamixel_Control\softFish\CV\Calibration\PixelDistancePhotos\WIN_20250721_13_11_42_Pro.jpg")  # or capture a frame from video
#known height of 9.84 cm, 98.4 mm
if img is None:
    raise ValueError("Failed to load image.")

#undistorts image
img_update=undistort(mtx, dist, img)
cv2.imshow('Image', img_update)
cv2.setMouseCallback('Image', click_event, param=img_update)
print("Click two points to measure pixel distance (Top and bottom of line).")

#will measure the straight line distance between top and bottom 
cv2.waitKey(0)
cv2.destroyAllWindows()

#registers two points have been clicked, then computes distance
if len(points) == 2:
    pt1 = np.array(points[0], dtype=np.float32)
    pt2 = np.array(points[1], dtype=np.float32)
    pixel_distance = np.linalg.norm(pt1 - pt2)
    print(f"Pixel distance between points: {pixel_distance:.2f} pixels")
else:
    print("You need to click exactly two points.")

#actual measured distance, converts to a pixel/cm ratio
actual_distance=9.84
pixel_per_cm=pixel_distance/actual_distance
print("Pixel per cm is", pixel_per_cm)

#head angle metrics csv
input_csv=r"C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\Fish_CV_Output\Head_Angle_Metrics.csv"
# Read the whole CSV into a DataFrame
df = pd.read_csv(input_csv)

#loads data, makes sure it is a float
column_data = (df.iloc[:, 3]) #want fourth column, index=3
cleaned_data=column_data[3:-1] #again, want the fourth row to end
# Ensure cleaned_data is numeric
cleaned_data = cleaned_data.astype(float)

#converts column from pixel to real (mm) distance
real_distance=(1/(pixel_per_cm))*cleaned_data #1/pixel_mm gives mm/pixel *pixel distance gives real distance
print("Real distances from pixel values:",real_distance)

#even if there is a pitch, it is so minor that it shouldn't drastically change the matrix values