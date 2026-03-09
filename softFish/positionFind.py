#goal is to output the current position of the dynamixel motor 

from dynamixel_sdk import *  # Uses Dynamixel SDK library

goal_pos=1238
goal_vel=100
# Control table address for Present Position
ADDR_PRESENT_POSITION = 132 # present position of the dynamixel motor
ADDR_GOAL_POSITION=116 # goal position of the dynamixel motor
ADDR_GOAL_VELOCITY=104 # goal velocity of the dynamixel motor
ADDR_TORQUE_ENABLE=64 # torque enable address
# Protocol version 2
PROTOCOL_VERSION = 2.0

# Device name (your USB2Dynamixel or equivalent port)
port = "/dev/ttyUSB1"

# Baudrate
BAUDRATE = 1000000

# Initialize PortHandler instance
portHandler = PortHandler(port)

# Initialize PacketHandler instance
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if not portHandler.openPort():
    print("Failed to open port")
    quit()
# Set baudrate
if not portHandler.setBaudRate(BAUDRATE):
    print("Failed to set baudrate")
    quit()

dxl_id = 1  # Your motor ID




# Read 4 bytes from Present Position address
present_position, comm_result, error = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
print(f"Current Position: {present_position}")

packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, 1)
position, _, _ = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_VELOCITY, goal_vel)
packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, goal_pos)
packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, 1)
print(f"Current Position: {present_position}")
#packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, 0)

portHandler.closePort()

"""
if comm_result != COMM_SUCCESS:
    print(f"Communication failed: {packetHandler.getTxRxResult(comm_result)}")
elif error != 0:
    print(f"Error occurred: {packetHandler.getRxPacketError(error)}")
else:
    print(f"Current Position: {present_position}")


"""


#position at zero is 1408