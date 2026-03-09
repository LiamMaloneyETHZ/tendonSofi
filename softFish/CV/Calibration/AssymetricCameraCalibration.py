# imports
import numpy as np
import cv2 as cv
import glob

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Generate correct 3D points for an asymmetric circle grid of size (columns, rows)
pattern_size = (4, 11)  # 4 columns, 11 rows
circle_spacing = 4  # cm, real world units for how far apart the circles are

obj3d = []
for j in range(pattern_size[1]):  # rows (11), had been [1]
    for i in range(pattern_size[0]):  # cols (4), had been [0]
        x = i * circle_spacing
        y = j * circle_spacing
        # odd rows are offset by half the spacing in x
        if j % 2 == 1:
            x += circle_spacing / 2
        obj3d.append([x, y, 0])

obj3d = np.array(obj3d, np.float32)

# Vector to store 3D points
obj_points = []
# Vector to store 2D points
img_points = []


# Extracting path of individual image stored in a given directory
images = glob.glob(r'C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\Dynamixel_Control\softFish\CV\Calibration\AssymetricCalibrationPhotos\*.jpg')

for f in images:
    # Loading image
    img = cv.imread(f)
    # Conversion to grayscale image
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # To find the position of circles in the grid pattern
    ret, corners = cv.findCirclesGrid(
        gray, (4, 11), None, flags=cv.CALIB_CB_ASYMMETRIC_GRID)

    # If true is returned, 
    # then 3D and 2D vector points are updated and corner is drawn on image
    if ret == True:
        obj_points.append(obj3d)

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        # In case of circular grids, 
        # the cornerSubPix() is not always needed, so alternative method is:
        # corners2 = corners
        img_points.append(corners2)

        # Drawing the corners, saving and displaying the image
        cv.drawChessboardCorners(img, (4, 11), corners2, ret)
        cv.imwrite('output.jpg', img) #To save corner-drawn image
        cv.imshow('img', img)
        cv.waitKey(0)
cv.destroyAllWindows()

"""Camera calibration: 
Passing the value of known 3D points (obj points) and the corresponding pixel coordinates 
of the detected corners (img points)"""
ret, camera_mat, distortion, rotation_vecs, translation_vecs = cv.calibrateCamera(
    obj_points, img_points, gray.shape[::-1], None, None)

print("Error in projection : \n", ret)
print("\nCamera matrix : \n", camera_mat)
print("\nDistortion coefficients : \n", distortion)
print("\nRotation vector : \n", rotation_vecs)
print("\nTranslation vector : \n", translation_vecs)

"""

Error in projection :
 3.9659724431753367

Camera matrix :
 [[6.85402255e+03 0.00000000e+00 9.53349510e+02]
 [0.00000000e+00 6.32972942e+03 5.34921515e+02]
 [0.00000000e+00 0.00000000e+00 1.00000000e+00]]

Distortion coefficients :
 [[ 1.93965100e+01  1.03302061e+03  6.03419410e-01 -6.17968976e-02
  -1.74216458e-01]]

Rotation vector :
 (array([[ 0.0174048 ],
       [ 1.49831286],
       [-2.75245867]]), array([[-0.03722549],
       [-1.42654761],
       [-2.78272216]]), array([[-0.15837365],
       [ 1.42921771],
       [-2.62527861]]), array([[-0.13855246],
       [ 1.41519964],
       [-2.63381887]]), array([[ 0.31598021],
       [-1.32883915],
       [-2.48303582]]), array([[ 0.3113053 ],
       [-1.31229551],
       [-2.48158259]]), array([[-0.4837131 ],
       [ 1.28327245],
       [-2.28046271]]), array([[ 0.48478865],
       [-1.21805381],
       [-2.30927127]]), array([[0.7527112 ],
       [1.03632783],
       [1.84312281]]), array([[0.75013147],
       [1.03232796],
       [1.84521117]]), array([[0.78285378],
       [1.00393725],
       [1.77167767]]), array([[0.77807627],
       [1.0107854 ],
       [1.78342052]]), array([[-0.54785909],
       [-1.21857736],
       [ 2.13357909]]), array([[0.53795204],
       [1.17988202],
       [2.21132872]]), array([[0.53347892],
       [1.20560301],
       [2.29093202]]), array([[0.53271122],
       [1.21688231],
       [2.30259043]]), array([[0.51823757],
       [1.21893491],
       [2.31901437]]), array([[0.41123478],
       [1.27337575],
       [2.45231164]]))

Translation vector :
 (array([[  7.89546547],
       [ -0.80850168],
       [665.85601973]]), array([[ 7.72319582e+00],
       [-4.78273785e-01],
       [ 6.42100457e+02]]), array([[  8.34519968],
       [ -1.04398161],
       [661.37999036]]), array([[  8.41947752],
       [ -1.03945329],
       [663.37329734]]), array([[  8.22516714],
       [ -1.05683356],
       [592.19512563]]), array([[  8.37003096],
       [ -1.22282517],
       [592.90170034]]), array([[  7.89852384],
       [ -1.9545582 ],
       [615.89179709]]), array([[  7.57597725],
       [ -1.4806144 ],
       [586.83155114]]), array([[  6.11769885],
       [-14.92894753],
       [539.06750114]]), array([[  6.03256995],
       [-14.9713229 ],
       [543.41029094]]), array([[  5.13774034],
       [-15.16891814],
       [529.23422976]]), array([[  5.20781246],
       [-15.14098547],
       [530.74472591]]), array([[ 12.35835637],
       [-12.35990908],
       [602.52226046]]), array([[ 12.95111714],
       [-11.2699476 ],
       [573.67307966]]), array([[ 14.18549513],
       [ -9.82903017],
       [557.69435241]]), array([[ 14.8112964 ],
       [ -9.94501503],
       [557.96823637]]), array([[ 15.19936299],
       [ -9.83160044],
       [565.04094258]]), array([[ 17.25722708],
       [ -7.26592181],
       [568.65812576]]))

"""