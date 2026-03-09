import dxlFuncs
import tlsFuncs

##Create dynamixel objects
headLS = dxlFuncs.dxlServo(id=3,ext=7000,ret=0)
tailLS = dxlFuncs.dxlServo(id=4,ext=7000,ret=0)

tlsFuncs.extend(headLS,tailLS)
tlsFuncs.pauseAndPrint(3)
tlsFuncs.retract(headLS,tailLS)
tlsFuncs.extend(headLS,tailLS)
tlsFuncs.retract(headLS,tailLS)
tlsFuncs.extend(headLS,tailLS)
tlsFuncs.retract(headLS,tailLS)
tlsFuncs.extend(headLS,tailLS)
tlsFuncs.retract(headLS,tailLS)

tlsFuncs.extend(headLS,tailLS)
tlsFuncs.retract(headLS,tailLS)
tlsFuncs.extend(headLS,tailLS)
tlsFuncs.retract(headLS,tailLS)

dxlFuncs.closePort()