import numpy as np
import cv2 as cv
import glob

#follows tutorial by https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html to calibrate a fish-eye lens back to a normal distribution. Need to store at least 10 photographs of a chessboard in the same file location as the script
#the pattern size is the m-1 x n-1 with m and n being the rows and columns of the board

pattern_size = (8, 11)  # inner corners for 9x12 squares
square_size = 30.0      # mm, size of each side of the chest board

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((pattern_size[0]*pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
objp[:, :2] *= square_size

objpoints = []
imgpoints = []

images = glob.glob(r'C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\Dynamixel_Control\softFish\CV\Calibration\ChessboardCalibrationPhotos\*.jpg')
print(f"Found {len(images)} images.")

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, corners = cv.findChessboardCorners(gray, pattern_size, None)

    if ret:
        corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        objpoints.append(objp)

        cv.drawChessboardCorners(img, pattern_size, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(300)
    else:
        print(f"Chessboard not found in {fname}")

if len(objpoints) > 0:
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)



#img = cv.imread(r"C:\Users\15405\OneDrive\Desktop\Career\ETHZ\ETHZ Work\HatBottle.jpg")
#h,  w = img.shape[:2]
#newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

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
#dst = cv.undistort(img, mtx, dist, None, newcameramtx)

# crop the image
#x, y, w, h = roi
#dst = dst[y:y+h, x:x+w]
#cv.imwrite('calibresult_1.png', dst)

print("MTX",mtx)
print("DIST",dist)
print("DST",dst)
print("RET",ret)
print("RVECS",rvecs)
print("TVECS",tvecs)
cv.destroyAllWindows()

"""
[Updated Parameters for our camera at 74.1 cm away]
MTX [[850.46282868   0.         926.47015089]
 [  0.         850.34124243 546.3733339 ]
 [  0.           0.           1.        ]]
DIST [[-3.20324366e-01  1.46621572e-01 -2.06803818e-03 -2.81291640e-04
  -6.95534360e-02]]
DST [[[180 193 202]
  [179 193 203]
  [179 194 203]
  ...
  [ 75  84  71]
  [ 74  82  71]
  [ 73  82  72]]

 [[180 192 202]
  [179 192 201]
  [179 193 202]
  ...
  [ 87  97  81]
  [ 83  93  79]
  [ 80  90  79]]

 [[180 192 202]
  [180 192 202]
  [180 193 202]
  ...
  [ 91 102  84]
  [ 90 101  85]
  [ 92 102  89]]

 ...

 [[160 176 182]
  [162 177 183]
  [163 177 183]
  ...
  [148  61   0]
  [148  61   0]
  [150  63   0]]

 [[162 177 183]
  [163 177 183]
  [163 177 183]
  ...
  [150  61   0]
  [150  63   0]
  [151  64   0]]

 [[163 177 183]
  [162 176 182]
  [162 176 182]
  ...
  [151  63   0]
  [152  63   0]
  [154  64   0]]]
RET 0.15570738484172458
RVECS (array([[-0.04112394],
       [-0.05950388],
       [ 1.60333494]]), array([[-0.04043984],
       [-0.05956471],
       [ 1.60348094]]), array([[-0.13284683],
       [-0.06819317],
       [ 1.74579203]]), array([[-0.15786987],
       [-0.07531782],
       [ 1.76308711]]), array([[-0.20454544],
       [-0.1019303 ],
       [ 1.85586054]]), array([[-0.19458754],
       [-0.09410363],
       [ 1.84324714]]), array([[-0.08633925],
       [-0.14008487],
       [ 1.93620388]]), array([[-0.09029385],
       [-0.14475479],
       [ 1.93843227]]), array([[-0.03695604],
       [-0.06535016],
       [ 1.60385404]]), array([[ 0.00984477],
       [-0.08975473],
       [ 1.60525491]]), array([[ 0.07391565],
       [-0.00525313],
       [ 1.50809497]]), array([[ 0.04477773],
       [-0.02451272],
       [ 1.49119149]]), array([[4.76446560e-02],
       [7.41099008e-04],
       [1.42010390e+00]]), array([[0.04610545],
       [0.00238584],
       [1.39534724]]), array([[ 0.04585558],
       [-0.00547396],
       [ 1.36285247]]), array([[0.0490808 ],
       [0.01278776],
       [1.32171261]]))
TVECS (array([[ 174.83749666],
       [-264.80766577],
       [ 783.06374691]]), array([[ 174.91141678],
       [-264.73368871],
       [ 783.11943824]]), array([[ 212.18705666],
       [-266.99488572],
       [ 794.95354232]]), array([[ 216.79404799],
       [-266.81028469],
       [ 797.74735276]]), array([[ 241.66923382],
       [-264.72918999],
       [ 801.92188765]]), array([[ 238.16351515],
       [-265.19057963],
       [ 801.58203421]]), array([[ 263.05487346],
       [-260.96506062],
       [ 779.12653626]]), array([[ 263.6950553 ],
       [-260.92921427],
       [ 779.37786488]]), array([[ 181.76713504],
       [-263.47229765],
       [ 781.83006137]]), array([[ 213.84921911],
       [-261.76438721],
       [ 769.30831753]]), array([[ 186.31775768],
       [-294.09309607],
       [ 737.08491504]]), array([[ 182.46633047],
       [-300.07779026],
       [ 749.63531163]]), array([[ 161.56354169],
       [-322.39866047],
       [ 747.13239325]]), array([[ 154.14158528],
       [-329.7839008 ],
       [ 747.55976749]]), array([[ 144.12708616],
       [-339.11056276],
       [ 747.92733216]]), array([[ 130.52926316],
       [-350.65412819],
       [ 746.32997222]]))


  """