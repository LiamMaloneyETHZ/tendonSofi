goal_freq=4.84 #goal velocity of the tail in hertz, max of 4.84335
motor_max_velo=235 
motor_velo_step=.229 #unit scale

gear_ratio=5.4 #for the planetary gear setup ratio of planets vs. sun +1
motor_freq=goal_freq/gear_ratio
motor_ticks=motor_freq/motor_velo_step #divides by unit scale, gives ticks
motor_velocity=motor_ticks*60 #converts to ticks per minute
velocity=int(round(motor_velocity)) #int cast

print(velocity)
if (velocity>motor_max_velo or velocity<-motor_max_velo):
    print("Max Motor Velocity Exceeded!")
else:
    print(f"Instructed motor velocity = {velocity}")

'''In the actual code use the below code:

goal_freq = 4.84 #goal velocity of the tail in hertz, max of 4.84335
motor_max_speed = 235 
motor_velo_step = 0.229 #unit scale
gear_ratio = 5.4 #for the planetary gear setup ratio of planets vs. sun +1
velocity = int(round(goal_freq/gear_ratio*60/motor_velo_step)) #conversion from desired output frequency to instructed motor velocity
if (velocity > motor_max_speed or velocity < -motor_max_speed):
    velocity = 0
    print("Max Motor Velocity Exceeded!")

'''