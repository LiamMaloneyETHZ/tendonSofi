import sys,os,configparser

def relativeDir(relPath):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dynamixel_control_path = os.path.join(script_dir, relPath)
    dynamixel_control_path = os.path.normpath(dynamixel_control_path)
    sys.path.append(dynamixel_control_path)

def motorZeroConfig(file_name = 'motor_zeros.ini'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, file_name)
    config = configparser.ConfigParser()
    config.read(config_path)
    return config, config_path