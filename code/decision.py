import numpy as np
import random


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def is_clear(Rover):
    #Verifying if the pixels in front of the over are mainly ground
    clear = (np.sum(Rover.vision_image[140:150,150:170,2]) > 130)\
     & (np.sum(Rover.vision_image[110:120,150:170,2]) > 100)\
     & (np.sum(Rover.vision_image[150:153,155:165,2]) > 20)
    return clear


def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Added Rover.navcount variable for tracking navigable vision data count 
        # Added Rover.isclearflag variable for checking if the terrain in front of the rover is free of obstacles.
        Rover.navcount =len(Rover.nav_angles)
        Rover.isclearflag=is_clear(Rover)
        # Check for Rover.mode status
        # check if there is no rock samples nearby and there is no rock vision data 
        if Rover.mode == 'forward'and len(Rover.rock_angles)==0 and Rover.near_sample ==0 :
            #Add a random steer angle to avoid loops
            Rover.random_steer = random.randint(-5,5)
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -20, 20) + Rover.random_steer
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward :
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        # Also check if there is no rock vision data and no rock sample nearby
        elif Rover.mode == 'stop' and len(Rover.rock_angles)==0 and Rover.near_sample == 0 :
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -25 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward :
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -20, 20)
                    Rover.mode = 'forward'

    # check if there is a vision data about rock sample
        elif len(Rover.rock_angles)!=0:
            #steer towards the rock sample 
            Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
            # if there is enough vision data for rock sample 
            if len(Rover.rock_angles) >= Rover.rock_threshold :
                #check if the velocity is less than 1, throttle at slower rate to reach the rock  
                if Rover.vel < 1:
                    Rover.throttle = 0.1
                    Rover.brake = 0
                # if the velocity is more than 1, stop throttle and apply brake at a steady rate 
                elif Rover.vel>=1 :
                    Rover.throttle =0
                    Rover.brake = 5
          
            elif len(Rover.rock_angles) < Rover.rock_threshold:
                # set appropiate velocity and apply brake to reach towards the rock sample 
                if Rover.vel < 0.7:
                    Rover.throttle= 0.1 
                    Rover.brake =0 
                elif Rover.vel >= 0.7:
                    Rover.throttle =0
                    Rover.brake = 5 
                # chekc if Rock sample is nearby.if yes adjust setting to reach to the rock sample
                if Rover.near_sample :
                    Rover.throttle=0
                    Rover.brake=Rover.brake_set
                    Rover.steer=0
                    #chekc if the Rover has stopped and Rover is not already busy picking up samples 
                    if Rover.vel==0 and not (Rover.picking_up):
                        # set the rock pick up flag to send the command 
                        Rover.send_pickup = True 
        # add logic for obstacle detection 
        elif not is_clear(Rover):
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                Rover.throttle = 0 
                Rover.brake = 0
                Rover.steer = -25
                Rover.mode = 'stop'
    # Just to make the rover do something 
    # even if no modifications have been made to the code              
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover

