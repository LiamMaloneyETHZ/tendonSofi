import numpy as np
import json
import cv2 as cv
import os

def pixel_to_real_distance(pixel_distance, image_path, calibration_file_path='./images/calibration_data.json', real_checkerboard_size_mm=30, checkerboard_size=(8, 11)):
    """
    Calculate the real-world distance in mm for a given pixel distance using calibration data.

    Args:
        pixel_distance (float): Distance in pixels to convert.
        image_path (str): Path to the image containing the checkerboard pattern.
        calibration_file_path (str): Path to the JSON file with calibration data.
        real_checkerboard_size_mm (float): Real-world size of one checkerboard square in mm.
        checkerboard_size (tuple): Number of inner corners per row and column on the checkerboard.

    Returns:
        float: Real-world distance in mm.
    """
    """
    # Load the saved camera calibration data from JSON
    if os.path.exists(calibration_file_path):
        with open(calibration_file_path, 'r') as f:
            calibration_data = json.load(f)
        camera_matrix = np.array(calibration_data['camera_matrix'])
        dist_coeffs = np.array(calibration_data['dist_coeffs'])
    else:
        raise FileNotFoundError(f"{calibration_file_path} not found.")
    """
    camera_matrix = np.array([
    [1.81568134e+04, 0.00000000e+00, 9.56161742e+02],
    [0.00000000e+00, 1.32721393e+04, 5.42345423e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
    ])

    dist_coeffs = np.array([
    [-8.42669229e+01, 1.67955964e+04, -2.19710745e-02, -3.01774375e-01, 1.78927085e+01]
    ])
    
    # Read the image specified in the argument
    img = cv.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Failed to load image at {image_path}")
    
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Find the checkerboard corners
    ret, corners = cv.findChessboardCorners(gray, checkerboard_size, None)
    
    if ret:
        # Refine corners
        corners2 = cv.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )
        #could parse through headscript and use those distances rather than the pixel_checkerboard_distance
        # Calculate the distance between two adjacent corners in the checkerboard
        pixel_checkerboard_distance = np.linalg.norm(corners2[0] - corners2[1])

        # Real-world distance (mm) per pixel
        #real_world_checkerboard_size_mm=30 and pixel_checkerboard_distance from corner to corner is
        mm_per_pixel = real_checkerboard_size_mm / pixel_checkerboard_distance

        # Convert the pixel distance to real-world distance in mm
        real_distance_mm = pixel_distance * mm_per_pixel
        return real_distance_mm
    else:
        raise Exception("Checkerboard not detected in the image!")
    
result = pixel_to_real_distance(
    100,
    "C:\\Users\\15405\\OneDrive\\Pictures\\Camera Roll\\WIN_20250717_13_33_09_Pro.jpg"
)


#could change the script to read the pixel distance between the head com and rigid body com and save them to a CSV 
print("The distance is: ",result)