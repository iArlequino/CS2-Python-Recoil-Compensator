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
VK_MENU = 0x12
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

returnBackAfterShooting = False

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
    'E': SmoothnessConf(1, [90000, 0], 2, [44500, 0], 5, [4000, 10000]),
    'D': SmoothnessConf(1, [90000, 0], 2, [44500, 0], 5, [4000, 10000]),
    'U': SmoothnessConf(1, [90000, 0], 2, [44500, 0], 5, [4000, 10000]), # UMP-45
    'G': SmoothnessConf(1, [90000, 0], 2, [44500, 0], 5, [4000, 10000]), # AUG
    'S': SmoothnessConf(1, [90000, 0], 2, [44500, 0], 5, [4000, 10000]), # SG553
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
    'E': Gun(25,
        [
            -12, 3, -18, -3, 0, 42, 48, -18, -60, -48, -39, 12, 69, 36, 60, 15, 45, 9, -12, -75, -9, 33, 45, 45, 0
        ],
        [
            15, 12, 30, 51, 60, 54, 36, 36, 24, 15, 6, 15, 12, 18, -9, 0, 0, 15, 9, -3, 6, 0, -21, -30, 0
        ]
    ),
    'D': Gun(35,
        [
            0, 0, 4, -2, 6, 12, -1, 2, 6, 11, -4, -22, -30, -29, -9, -12, -7, 0, 4, 25, 14, 25, 31, 6, -12, 13, 10, 16, -9, -32, -24, -15, 6, -14, -24
        ],
        [
            0, 0, 4, 5, 10, 15, 21, 24, 16, 10, 14, 8, -3, -13, 8, 2, 1, 1, 7, 7, 4, -3, -9, 3, 3, -1, -1, -4, 5, -5, -3, 5, 8, -3, -14
        ]
    ),
    'U': Gun(32,
        [
            x * 2.5 for x in [
                0, -1, -4, -2, -4, -9, -3, 11, -4, 9, 18, 15, -1, 5, 0, 9, 5, -12, -19, -1, 15, 17, -6, -20, -3, 0, 15, 17, -6, -20, -3, 0
            ]
        ],
        [
            y * 2.5 for y in [
                0, 6, 8, 18, 23, 23, 26, 17, 12, 13, 8, 5, 3, 6, 6, -3, -1, -2, -5, -5, -5, -2, 3, -2, -1, 6, -5, -2, 3, -2, -1, 6
            ]
        ]
    ),
    'G': Gun(32,
        [
            x * 2.0 for x in [
                5, 0, -5, -7, 5, 9, 14, 6, 14, -16, -5, 13, 1, -22, -38, -31, -3, -5, -9, 24, 32, 15, -5, 17, 29, 19, -16, -16, -4, 0, 0, 0
            ]
        ],
        [
            y * 2.0 for y in [
                6, 13, 22, 26, 29, 30, 21, 15, 13, 11, 6, 0, 6, 5, -11, -13, 6, 5, 0, 1, 3, 6, 1, -3, -11, 0, 6, 3, 1, 0, 0, 0
            ]
        ]
    ),
    'S': Gun(32,
        [
            x * 2.0 for x in [
                -4, -13, -9, -6, -8, -7, -20, 14, -8, -15, -5, 6, -8, 2, -14, -20, -18, -8, 41, 56, 43, 18, 14, 6, 21, 29, -6, -15, -38, 0, 0, 0
            ]
        ],
        [
            y * 2.0 for y in [
                9, 15, 25, 29, 31, 36, 14, 17, 12, 8, 5, 5, 6, 11, -6, -17, -9, -2, 3, -5, -1, 9, 9, 7, -3, -4, 8, 5, -5, 0, 0, 0
            ]
        ]
    ),
}

def FindTotalDisplacement(EitherXorY, CountValueStoppedAt, XorY):
    total = 0
    for i in range(CountValueStoppedAt):
        for _ in range(CurrentSmoothness):
            total += EitherXorY[i] / CurrentSmoothness
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
    inp.type = 0
    inp.mi = MOUSEINPUT(NormalizedX, NormalizedY, 0, 0x0001, 0, None)
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def generateNumber():
    return 0.8 + random.random() * (1.2 - 0.8)

def returnBackAfterComp(X, Y, FullfinishOrMidFinish, delay):
    DivisionXFix = FindTotalDisplacement(X, count + 1, 0) - ((FindTotalDisplacement(X, count + 1, 0) / returnBackSmoothness) * returnBackSmoothness)
    DivisionYFix = FindTotalDisplacement(Y, count + 1, 1) - ((FindTotalDisplacement(Y, count + 1, 1) / returnBackSmoothness) * returnBackSmoothness)
    for _ in range(returnBackSmoothness):
        moveMouse(round((FindTotalDisplacement(X, count + 1, 0) / returnBackSmoothness) / randomNumber),
                 round((FindTotalDisplacement(Y, count + 1, 1) / returnBackSmoothness) / randomNumber))
        time.sleep(delay / 1000.0)
    moveMouse(round(DivisionXFix / randomNumber), round(DivisionYFix / randomNumber))

def SmoothMovementMove(X, Y, delay, smoothness):
    for _ in range(smoothness):
        time.sleep(delay[0] / 1_000_000)
        moveMouse(round((X[count] / smoothness) / randomNumber), 
                 round((Y[count] / smoothness) / randomNumber))
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
    elif CurrentWeaponIndex == 4:
        gun = Guns['E']
        CurrentGunName = "FAMAS"
    elif CurrentWeaponIndex == 5:
        gun = Guns['D']
        CurrentGunName = "Galil"
    elif CurrentWeaponIndex == 6:
        gun = Guns['U']
        CurrentGunName = "UMP-45"
    elif CurrentWeaponIndex == 7:
        gun = Guns['G']
        CurrentGunName = "AUG"
    elif CurrentWeaponIndex == 8:
        gun = Guns['S']
        CurrentGunName = "SG553"
    else:
        return
    CurrentRawWeaponX = gun.RawX
    CurrentRawWeaponY = gun.RawY
    CurrentWeaponX = gun.X
    CurrentWeaponY = gun.Y
    CurrentSize = gun.size
    for k in range(CurrentSize):
        if CS2sensitivity != 0:
            if CurrentGunName == "Galil":
                modifier = 2.52 / CS2sensitivity
                CurrentWeaponX[k] = CurrentRawWeaponX[k] * modifier  
                CurrentWeaponY[k] = CurrentRawWeaponY[k] * modifier
            else:
                CurrentWeaponX[k] = CurrentRawWeaponX[k] / CS2sensitivity
                CurrentWeaponY[k] = CurrentRawWeaponY[k] / CS2sensitivity
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

macroMode = 1

def DisplayStatusConfig(StatusIndex):
    os.system('cls' if os.name == 'nt' else 'clear')
    if StatusIndex == 1:
        print("CS2 NoRecoil")
        print(f"{CS2sensitivity=}".replace("CS2sensitivity=", "Selected sensitivity: "))
        print(f"Selected mode: {'F1 - Cycle' if macroMode == 1 else 'Hotkeys'}")
        print()
        print("-------------------------------------------")
        print()
        print(f"|Weapon selection: {CurrentGunName}")
        print(f"|Smoothness selection: {CurrentSmoothnessName}")
        print(f"|Randomizer: {randomizer}")
        print(f"|Return after shooting: {returnBackAfterShooting}")
        print(f"|NoRecoil Key: {keyNames[currentKeyIndex - 1]}")
        print(f"|Stop Key: CapsLock")
        print()
        print("-------------------------------------------")
        print()
        print("|Weapon hotkeys (mode 2): AK-F5, M4A4-F6, M4A1S-F7, FAMAS-F8, Galil-F9, UMP-45-F11, AUG-HOME, SG553-END")
        print("|Switch macro mode: PAGE_DOWN")
        print()
        print("-------------------------------------------")
    elif StatusIndex == 2:
        print("Static set keybinds :\n \nF1 Cycle Guns, F2 Cycle Smoothness,\nF3 Enable/Disable Randomness, \nF4 Enable/Disable Aim Return, \nEND Quit \n")
        print("\n \n \nKEY SWITCHING MODE, GO THROUGH OPTIONS USING LEFT/RIGHT ARROW KEYS ")
        print("TO APPLY CHANGES TO CURRENT SELECTION/EXIT, PRESS AGAIN H ")
        print("\n-----NoRecoil Key-----")
        print(f"Current selection : {keyNames[currentKeyIndex - 1]}")
        print(f"Current macro mode: {'F1 - Cycle' if macroMode == 1 else 'F5-F9 - Hotkeys'}")
        print("|Weapon hotkeys (mode 2): AK-F5, M4A4-F6, M4A1S-F7, FAMAS-F8, Galil-F9, UMP-45-F11, AUG-HOME, SG553-END")
        print("|Switch macro mode: PAGE_DOWN")
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

def startup_animation():
    import sys
    bar_length = 30
    for i in range(bar_length + 1):
        percent = int((i / bar_length) * 100)
        bar = '█' * i + '-' * (bar_length - i)
        sys.stdout.write(f"\r\033[STARTING] |{bar}| {percent}%\033")
        sys.stdout.flush()
        time.sleep(0.045 + random.uniform(0, 0.03))
    print("\n\033[Welcome!\033")
    time.sleep(0.7)
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    import keyboard

    startup_animation()

    global CS2sensitivity, CurrentWeaponIndex, CurrentSmoothnessIndex, randomizer, randomNumber, returnBackAfterShooting, NoRecoilStatus, macroMode

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

        if keyboard.is_pressed('page down'):
            while keyboard.is_pressed('page down'):
                time.sleep(0.05)
            macroMode = 2 if macroMode == 1 else 1
            DisplayStatusConfig(1)

        if keyboard.is_pressed('f2'):
            while keyboard.is_pressed('f2'):
                time.sleep(0.05)
            CurrentSmoothnessIndex += 1
            if CurrentSmoothnessIndex == 4:
                CurrentSmoothnessIndex = 1
            ScrollThroughSmoothness()

        if keyboard.is_pressed('f3'):
            while keyboard.is_pressed('f3'):
                time.sleep(0.05)
            randomizer = not randomizer
            if not randomizer:
                randomNumber = 1
            DisplayStatusConfig(1)

        if keyboard.is_pressed('f4'):
            while keyboard.is_pressed('f4'):
                time.sleep(0.05)
            returnBackAfterShooting = not returnBackAfterShooting
            DisplayStatusConfig(1)

        if macroMode == 1:
            if keyboard.is_pressed('f1'):
                while keyboard.is_pressed('f1'):
                    time.sleep(0.05)
                CurrentWeaponIndex += 1
                if CurrentWeaponIndex == 9:
                    CurrentWeaponIndex = 1
                ScrollThroughWeapons()
        else:
            if keyboard.is_pressed('f5'):
                while keyboard.is_pressed('f5'):
                    time.sleep(0.05)
                CurrentWeaponIndex = 1
                ScrollThroughWeapons()
            elif keyboard.is_pressed('f6'):
                while keyboard.is_pressed('f6'):
                    time.sleep(0.05)
                CurrentWeaponIndex = 2
                ScrollThroughWeapons()
            elif keyboard.is_pressed('f7'):
                while keyboard.is_pressed('f7'):
                    time.sleep(0.05)
                CurrentWeaponIndex = 3
                ScrollThroughWeapons()
            elif keyboard.is_pressed('f8'):
                while keyboard.is_pressed('f8'):
                    time.sleep(0.05)
                CurrentWeaponIndex = 4
                ScrollThroughWeapons()
            elif keyboard.is_pressed('f9'):
                while keyboard.is_pressed('f9'):
                    time.sleep(0.05)
                CurrentWeaponIndex = 5
                ScrollThroughWeapons()
            elif keyboard.is_pressed('f11'):
                while keyboard.is_pressed('f11'):
                    time.sleep(0.05)
                CurrentWeaponIndex = 6
                ScrollThroughWeapons()
            elif keyboard.is_pressed('home'):
                while keyboard.is_pressed('home'):
                    time.sleep(0.05)
                CurrentWeaponIndex = 7
                ScrollThroughWeapons()
            elif keyboard.is_pressed('end'):
                while keyboard.is_pressed('end'):
                    time.sleep(0.05)
                CurrentWeaponIndex = 8
                ScrollThroughWeapons()

        if keyboard.is_pressed('insert'):
            while keyboard.is_pressed('insert'):
                time.sleep(0.05)
            NoRecoilStatus = not NoRecoilStatus
            SwitchKeyBind()
            DisplayStatusConfig(1)
            NoRecoilStatus = not NoRecoilStatus

    os._exit(0)

if __name__ == "__main__":
    main()