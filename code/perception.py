import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    obs_select = np.zeros_like(img[:,:,0])
    rock_select = np.zeros_like(img[:,:,0])
    rock_thresh=(100,100,50)
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    navig_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    obs_thresh = (img[:,:,0] < rgb_thresh[0]) \
                & (img[:,:,1] < rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])
    rocksample_thresh = (img[:,:,0] > rock_thresh[0]) \
                & (img[:,:,1] > rock_thresh[1]) \
                & (img[:,:,2] < rock_thresh[2])
    # print(above_thresh)
    # Index the array of zeros with the boolean array and set to 1
    color_select[navig_thresh] = 1
    obs_select[obs_thresh] = 1
    rock_select[rocksample_thresh] = 1
    return color_select,obs_select,rock_select
#threshed = color_thresh(warped)

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    out_of_view =  cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))
    return warped, out_of_view

# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    
    dst_size = 5 
    bottom_offset = 6
    image=Rover.img
    xpos,ypos = Rover.pos

    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                  [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  ])
    # 2) Apply perspective transform
    warped,out_of_view = perspect_transform(image, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    threshed,obs,rock = color_thresh(warped)
    obs_map=np.absolute(np.float32(obs)-1)*out_of_view
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image

    Rover.vision_image[:,:,0] = obs_map*255
    Rover.vision_image[:,:,1] = rock*255
    Rover.vision_image[:,:,2] = threshed*255
    # 5) Convert map image pixel values to rover-centric coords
    xpix_t, ypix_t = rover_coords(threshed)
    xpix_obs, ypix_obs = rover_coords(obs)
    xpix_rock, ypix_rock = rover_coords(rock)
    # 6) Convert rover-centric pixel values to world coordinates
    world_size = Rover.worldmap.shape[0]
    scale = 2 * dst_size
    xpix_world,ypix_world = pix_to_world(xpix_t, ypix_t, xpos, ypos, Rover.yaw, world_size, scale)
    obs_xpix_world,obs_ypix_world = pix_to_world(xpix_obs, ypix_obs, xpos,ypos, Rover.yaw, world_size, scale)
    rock_xpix_world,rock_ypix_world = pix_to_world(xpix_rock, ypix_rock,xpos,ypos, Rover.yaw, world_size, scale)
    
    
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    Rover.worldmap[obs_ypix_world, obs_xpix_world, 0] += 50
    Rover.worldmap[rock_ypix_world, rock_xpix_world, 1] +=50 
    Rover.worldmap[ypix_world,xpix_world, 2] += 50

    # 8) Convert rover-centric pixel positions to polar coordinates
    rover_centric_distances,rover_centric_angles = to_polar_coords(xpix_t, ypix_t)
    rock_distances,rock_angles = to_polar_coords(xpix_rock, ypix_rock)
    # Update Rover and rock  pixel distances and angles
    Rover.nav_dists = rover_centric_distances
    Rover.nav_angles = rover_centric_angles
    Rover.rock_dist = rock_distances
    Rover.rock_angles = rock_angles
    
 
    
    
    return Rover