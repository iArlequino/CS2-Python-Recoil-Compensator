import ctypes
import threading
import time
import random
import math
import os

NoRecoilStatus = True

VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_XBUTTON1 = 0x05
VK_XBUTTON2 = 0x06
VK_BACK = 0x08
VK_CONTROL = 0x11
VK_MENU = 0x12  # ALT
VK_X = 0x58
VK_Y = 0x59
VK_Z = 0x5A

NoRecoilKey = VK_LBUTTON
keyNames = ["LBUTTON", "RBUTTON", "MBUTTON", "X1BUTTON", "X2BUTTON", "BACKSPACE", "CTRL", "ALT", "X", "Y", "Z"]
keyCodes = [VK_LBUTTON, VK_RBUTTON, VK_MBUTTON, VK_XBUTTON1, VK_XBUTTON2, VK_BACK, VK_CONTROL, VK_MENU, VK_X, VK_Y, VK_Z]
currentKeyIndex = 1

count = 0
returnBackSmoothness = 15
returnDelay = 1

CurrentSmoothnessIndex = 1
CurrentSmoothness = 1
CurrentSmoothnessDelay = [100000, 0]
CurrentSmoothnessName = " "

CurrentWeaponIndex = 1
CurrentSize = 0
CurrentRawWeaponX = None
CurrentRawWeaponY = None
CurrentWeaponX = None
CurrentWeaponY = None
CurrentGunName = " "

CS2sensitivity = 0.0
randomizer = False
randomNumber = 1.0

returnBackAfterShooting = True

class SmoothnessConf:
    def __init__(self, rigid, rigidDelay, semiRigid, semiRigidDelay, soft, softDelay):
        self.rigid = rigid
        self.rigidDelay = rigidDelay
        self.semiRigid = semiRigid
        self.semiRigidDelay = semiRigidDelay
        self.soft = soft
        self.softDelay = softDelay

SmoothnessConfiguration = {
    'A': SmoothnessConf(1, [100000, 0], 2, [25000, 40000], 5, [4000, 20000]),
    'B': SmoothnessConf(1, [90000, 0], 2, [44500, 0], 5, [4000, 10000]),
    'C': SmoothnessConf(1, [90000, 0], 2, [44500, 0], 5, [4000, 10000]),
}

class Gun:
    def __init__(self, size, RawX, RawY):
        self.size = size
        self.RawX = RawX
        self.RawY = RawY
        self.X = [0] * size
        self.Y = [0] * size

Guns = {
    'A': Gun(31,
        [0, 0, 0, 0, 0, 40, 40, -40, -90, -30, -20, -20, -20, 0, 80, 30, 50, 50, 30, 20, -20, -10, 0, 10, 0, -40, -90, -70, -30, -10, 0],
        [0, 40, 40, 80, 80, 80, 80, 20, -10, 20, 0, 0, -10, 20, 30, -10, 20, 0, -10, -10, 10, 10, 10, 0, 10, -10, 0, -50, 10, -10, 0]
    ),
    'B': Gun(31,
        [0, 0, 0, 0, 0, -10, 10, 20, 20, 30, -40, -40, -40, -40, -40, -50, 0, 30, 30, 20, 60, 30, 40, 20, 10, 0, 0, 10, 10, 0, 0],
        [0, 10, 30, 40, 40, 60, 60, 60, 30, 20, 20, 20, 0, -10, 0, 10, 10, 0, 0, 0, 10, 0, 0, 10, 0, 10, 10, 0, 0, 0, 0]
    ),
    'C': Gun(26,
        [0, 0, 0, 0, 0, -10, 0, 30, 10, 30, -10, -40, -20, -30, -20, -20, -30, -30, 10, -10, 0, 20, 40, 60, 10, 0],
        [0, 10, 10, 30, 30, 40, 40, 50, 10, 10, 10, 20, 0, -10, 0, 0, -10, 0, 10, 0, 10, 0, 0, 20, 0, 0]
    ),
}

def FindTotalDisplacement(EitherXorY, CountValueStoppedAt, XorY):
    # XorY: 0 - X, 1 - Y
    total = 0
    for i in range(CountValueStoppedAt):
        for _ in range(CurrentSmoothness):
            total += EitherXorY[i] // CurrentSmoothness
    total = -(total - EitherXorY[0])
    return total

def moveMouse(NormalizedX, NormalizedY):
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                    ("mi", MOUSEINPUT)]
    inp = INPUT()
    inp.type = 0  # INPUT_MOUSE
    inp.mi = MOUSEINPUT(NormalizedX, NormalizedY, 0, 0x0001, 0, None)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def generateNumber():
    return 0.8 + random.random() * (1.2 - 0.8)

def returnBackAfterComp(X, Y, FullfinishOrMidFinish, delay):
    DivisionXFix = FindTotalDisplacement(X, count + 1, 0) - ((FindTotalDisplacement(X, count + 1, 0) // returnBackSmoothness) * returnBackSmoothness)
    DivisionYFix = FindTotalDisplacement(Y, count + 1, 1) - ((FindTotalDisplacement(Y, count + 1, 1) // returnBackSmoothness) * returnBackSmoothness)
    for _ in range(returnBackSmoothness):
        moveMouse(int((FindTotalDisplacement(X, count + 1, 0) // returnBackSmoothness) / randomNumber),
                  int((FindTotalDisplacement(Y, count + 1, 1) // returnBackSmoothness) / randomNumber))
        time.sleep(delay / 1000.0)
    moveMouse(int(DivisionXFix / randomNumber), int(DivisionYFix / randomNumber))

def SmoothMovementMove(X, Y, delay, smoothness):
    for _ in range(smoothness):
        time.sleep(delay[0] / 1_000_000)
        moveMouse(int((X[count] / smoothness) / randomNumber), int((Y[count] / smoothness) / randomNumber))
    time.sleep(delay[1] / 1_000_000)

def ScrollThroughSmoothness():
    global CurrentSmoothnessName, CurrentSmoothness, CurrentSmoothnessDelay
    idx = (CurrentWeaponIndex - 1)
    gun_key = list(Guns.keys())[idx]
    conf = SmoothnessConfiguration[gun_key]
    if CurrentSmoothnessIndex == 1:
        CurrentSmoothnessName = "Rigid"
        CurrentSmoothness = conf.rigid
        CurrentSmoothnessDelay = conf.rigidDelay[:]
    elif CurrentSmoothnessIndex == 2:
        CurrentSmoothnessName = "Semi Rigid"
        CurrentSmoothness = conf.semiRigid
        CurrentSmoothnessDelay = conf.semiRigidDelay[:]
    elif CurrentSmoothnessIndex == 3:
        CurrentSmoothnessName = "Soft"
        CurrentSmoothness = conf.soft
        CurrentSmoothnessDelay = conf.softDelay[:]
    DisplayStatusConfig(1)

def ScrollThroughWeapons():
    global CurrentGunName, CurrentRawWeaponX, CurrentRawWeaponY, CurrentWeaponX, CurrentWeaponY, CurrentSize
    if CurrentWeaponIndex == 1:
        gun = Guns['A']
        CurrentGunName = "AK47"
    elif CurrentWeaponIndex == 2:
        gun = Guns['B']
        CurrentGunName = "M4A4"
    elif CurrentWeaponIndex == 3:
        gun = Guns['C']
        CurrentGunName = "M4A1-S"
    else:
        return
    CurrentRawWeaponX = gun.RawX
    CurrentRawWeaponY = gun.RawY
    CurrentWeaponX = gun.X
    CurrentWeaponY = gun.Y
    CurrentSize = gun.size
    for k in range(CurrentSize):
        if CS2sensitivity != 0:
            CurrentWeaponX[k] = round(10 * (CurrentRawWeaponX[k] / CS2sensitivity)) / 10
            CurrentWeaponY[k] = round(10 * (CurrentRawWeaponY[k] / CS2sensitivity)) / 10
        else:
            CurrentWeaponX[k] = CurrentRawWeaponX[k]
            CurrentWeaponY[k] = CurrentRawWeaponY[k]
    ScrollThroughSmoothness()
    DisplayStatusConfig(1)

def SwitchKeyBind():
    global currentKeyIndex, NoRecoilKey
    DisplayStatusConfig(2)
    import keyboard
    while True:
        time.sleep(0.01)
        if keyboard.is_pressed('right'):
            currentKeyIndex += 1
            if currentKeyIndex == 12:
                currentKeyIndex = 1
            DisplayStatusConfig(2)
        elif keyboard.is_pressed('left'):
            currentKeyIndex -= 1
            if currentKeyIndex == 0:
                currentKeyIndex = 11
            DisplayStatusConfig(2)
        elif keyboard.is_pressed('h'):
            break
    NoRecoilKey = keyCodes[currentKeyIndex - 1]

def DisplayStatusConfig(StatusIndex):
    os.system('cls' if os.name == 'nt' else 'clear')
    if StatusIndex == 1:
        print("CS2 NoRecoil")
        print("-------------------------------------------")
        print(f"|Current weapon selection: {CurrentGunName}")
        print(f"|Current smoothness selection: {CurrentSmoothnessName}")
        print(f"|Randomizer is set to {randomizer}")
        print(f"|Returning after shooting is set to {returnBackAfterShooting}")
        print(f"|Current NoRecoil Key: {keyNames[currentKeyIndex - 1]}")
        print(f"|Stop Key: CapsLock")
        print("-------------------------------------------")
    elif StatusIndex == 2:
        print("Static set keybinds :\n \nF1 Cycle Guns, F2 Cycle Smoothness,\nF3 Enable/Disable Randomness, \nF4 Enable/Disable Aim Return, \nEND Quit \n")
        print("\n \n \nKEY SWITCHING MODE, GO THROUGH OPTIONS USING LEFT/RIGHT ARROW KEYS ")
        print("TO APPLY CHANGES TO CURRENT SELECTION/EXIT, PRESS AGAIN H ")
        print("\n-----NoRecoil Key-----")
        print(f"Current selection : {keyNames[currentKeyIndex - 1]}")
    else:
        print("Unknown Status Display Index")

def is_key_pressed(vk_code):
    return ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000 != 0

def is_capslock_on():
    return ctypes.windll.user32.GetKeyState(0x14) & 1

def MainThread():
    global count, randomNumber
    while True:
        if is_capslock_on():
            time.sleep(0.05)
            continue
        if not NoRecoilStatus:
            time.sleep(0.05)
            continue
        if not is_key_pressed(NoRecoilKey):
            if count != 0:
                if returnBackAfterShooting:
                    returnBackAfterComp(CurrentWeaponX, CurrentWeaponY, 0, returnDelay)
                count = 0
                if randomizer:
                    randomNumber = generateNumber()
                continue
        else:
            if count == CurrentSize - 1:
                if returnBackAfterShooting:
                    returnBackAfterComp(CurrentWeaponX, CurrentWeaponY, 0, returnDelay)
                count = 0
                if randomizer:
                    randomNumber = generateNumber()
                time.sleep(0.5)
                continue
            count += 1
            SmoothMovementMove(CurrentWeaponX, CurrentWeaponY, CurrentSmoothnessDelay, CurrentSmoothness)

def main():
    import keyboard

    for i in range(15):
        print(chr(91 + i))
        time.sleep(0.01)
        os.system('cls' if os.name == 'nt' else 'clear')

    global CS2sensitivity, CurrentWeaponIndex, CurrentSmoothnessIndex, randomizer, randomNumber, returnBackAfterShooting, NoRecoilStatus

    try:
        CS2sensitivity = float(input("Please enter your CS2 sensitivity: "))
    except Exception:
        CS2sensitivity = 1.0

    ScrollThroughWeapons()

    t = threading.Thread(target=MainThread, daemon=True)
    t.start()

    random.seed(int(time.time()))

    while True:
        time.sleep(0.015)

        if keyboard.is_pressed('end'):
            print("!Goodbye!")
            time.sleep(0.3)
            break

        elif keyboard.is_pressed('f1'):
            while keyboard.is_pressed('f1'):
                time.sleep(0.05)
            CurrentWeaponIndex += 1
            if CurrentWeaponIndex == 4:
                CurrentWeaponIndex = 1
            ScrollThroughWeapons()

        elif keyboard.is_pressed('f2'):
            while keyboard.is_pressed('f2'):
                time.sleep(0.05)
            CurrentSmoothnessIndex += 1
            if CurrentSmoothnessIndex == 4:
                CurrentSmoothnessIndex = 1
            ScrollThroughSmoothness()

        elif keyboard.is_pressed('f3'):
            while keyboard.is_pressed('f3'):
                time.sleep(0.05)
            randomizer = not randomizer
            if not randomizer:
                randomNumber = 1
            DisplayStatusConfig(1)

        elif keyboard.is_pressed('f4'):
            while keyboard.is_pressed('f4'):
                time.sleep(0.05)
            returnBackAfterShooting = not returnBackAfterShooting
            DisplayStatusConfig(1)

        elif keyboard.is_pressed('h'):
            while keyboard.is_pressed('h'):
                time.sleep(0.05)
            NoRecoilStatus = not NoRecoilStatus
            SwitchKeyBind()
            DisplayStatusConfig(1)
            NoRecoilStatus = not NoRecoilStatus

    os._exit(0)

if __name__ == "__main__":
    main()