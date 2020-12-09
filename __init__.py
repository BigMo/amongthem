import sys
import ctypes
import time
import os
import signal
import random
from typing import Tuple
from PIL import ImageTk, Image
from threading import Thread
from tkinter import Tk, Canvas, W, NW, SW, SE, NE

from pymem import Pymem, pattern
import pymem
import os

from gamedata import DATA
from gametypes import IPlainRoom
from game import GAME, StaticVector
from helpers import Hotkeys


TPTARGETPL = 0
TPTARGETRO = 0

COLORS = ['#c61111', '#132ed2', '#11802d',
          '#ee54bb', '#f07d0d', '#f6f657', '#3f474e', '#d7e1f1', '#6b2fbc', '#71491e', '#38ffdd', '#50f039']
MAPS = {
    0: {
        'image': None,
        'center': (540 * 0.5, 150 * 0.5),
        'size': (abs(-37.7 - 50) * 0.5, abs(-30 - 18) * 0.5)
    },
    1: {
        'image': None,
        'center': (124 * 0.5, 468 * 0.5),
        'size': (abs(-10 - 62) * 0.5, abs(-6.6 - 53) * 0.5)
    },
    2: {
        'image': None,
        'center': (-5 * 0.5, 0 * 0.5),
        'size': (abs(0.8 - 82) * 0.5, abs(-54 - 0) * 0.5)
    }
}

ANONYMOUS = True
SHOWGHOSTS = True
CLICKTP = False
REVEALIMPOSTER = False
WALKPATH = False
IMPOSTER = False
NOCLIP = False
SPEEDHACK = False
SHOWHOTKEYS = True
SPEED = 1.5
WINDOW = None

DEADPLAYERS = []


def currentTpTarget():
    return GAME.allPlayers[TPTARGETPL] if GAME.allPlayers and TPTARGETPL < len(GAME.allPlayers) else None


def currentTpTargetRoom() -> IPlainRoom:
    return GAME.shipRooms[TPTARGETRO] if GAME.shipRooms and TPTARGETRO < len(GAME.shipRooms) else None


def drawmap(_canvas_: Canvas):
    global MAPS
    global ANONYMOUS
    global DEADPLAYERS
    global SHOWGHOSTS
    global SPEED
    global REVEALIMPOSTER
    global WALKPATH
    global IMPOSTER
    global NOCLIP
    global SPEEDHACK
    global CLICKTP
    global SHOWHOTKEYS
    global TASKPOS
    global WINDOW

    map = MAPS[GAME.shipStatus.MapType] if GAME.shipStatus else None
    _heightOffset = 240 if SHOWHOTKEYS else 40

    UI_TEXT = """Hotkeys:
[Shift] - Hold for Speedhack [{SH}]
[Plus] - Increase Speed +0.5
[Ctrl] - Hold for Click TP [{CT}]
[Alt] - Noclip [{NC}]
[F1] - Impostor [{I}]
[F2] - Complete all tasks
[F3] - Anonymous Mode [{AM}]
[F4] - Show Ghosts [{SG}]
[F5] - Reveal Imposter [{RI}]
[F6] - Walk path [{WP}]
[F8] - Hide Hotkeys
[F10] - Quit
""".format(
        SH='ON' if SPEEDHACK else 'OFF',
        CT='ON' if CLICKTP else 'OFF',
        NC='ON' if NOCLIP else 'OFF',
        I='ON' if IMPOSTER else 'OFF',
        AM='ON' if ANONYMOUS else 'OFF',
        SG='ON' if SHOWGHOSTS else 'OFF',
        RI='ON' if REVEALIMPOSTER else 'OFF',
        WP='ON' if WALKPATH else 'OFF')

    _canvas_.create_text(_canvas_.winfo_width() - 5, _canvas_.winfo_height() - _heightOffset, anchor=NE, font="Arial",
                         text=f'Speed: {SPEED}')

    if SHOWHOTKEYS:
        _canvas_.create_text(5, _canvas_.winfo_height() - _heightOffset,
                             anchor=NW, font="Arial", text=UI_TEXT)
    else:
        _canvas_.create_text(5, _canvas_.winfo_height() - _heightOffset,
                             anchor=NW, font="Arial", text='Hotkeys:\n[F8] - Show Hotkeys')

    if map:
        size = (map['image'].width(), map['image'].height())
        scale = (map['image'].width(
        ) / map['size'][0], map['image'].height() / map['size'][1])
        if _canvas_.winfo_width() != size[0] or _canvas_.winfo_height() != size[1]:
            _canvas_.config(width=size[0], height=size[1]+_heightOffset)
            rect = GetWindowRectFromName('Among Us')
            WINDOW.geometry(
                f'{_canvas_.winfo_width()}x{_canvas_.winfo_height()}+{rect[0]-8}+{rect[1] + rect[3] - _canvas_.winfo_height() - 32}')

        center = map['center']

        def _create_circle(self, x, y, r, **kwargs):
            return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

        _canvas_.create_image(0, 0, image=map['image'], anchor=NW)

        def translateVec(vec) -> Tuple[float, float]:
            return (center[0] + vec.X * scale[0],
                    (center[1] - vec.Y * scale[1]))

        if not ANONYMOUS and WALKPATH:
            for p in [p for p in GAME.allPlayers if not p.PlayerData.isDead]:
                _his = GAME.playerPositions.get(p.PlayerId)
                if _his and len(_his.items) > 1:
                    dpts = [translateVec(p) for p in _his.items]
                    pts = [p for v in dpts for p in v]
                    _canvas_.create_line(
                        *pts, fill=COLORS[p.PlayerData.colorId], width=3, smooth=True)
                    _canvas_.create_line(
                        *pts, fill=COLORS[p.PlayerData.colorId], smooth=True)
        if len(GAME.allPlayers) == 0:
            DEADPLAYERS.clear()
        for p in GAME.allPlayers:
            deadPlayer = manageDeadPlayer(p)
            drawposDead = None
            deadPlayerObj = None
            playerName = p.Name
            pos = p.NetworkTransform.TargetSyncPos if p.PlayerId != GAME.localPlayer.PlayerId else p.NetworkTransform.PrevPosSend
            if deadPlayer:
                deadPlayerObj = getDeadPlayer(p)
                drawposDead = translateVec(
                    deadPlayerObj.NetworkTransform.TargetSyncPos)

            drawpos = translateVec(pos)

            if REVEALIMPOSTER and p.PlayerData.isImpostor:
                playerName = f'[IMP] {p.Name}'
            if deadPlayer:
                timediff = time.time() - deadPlayerObj.killTimer
                if timediff < 40:
                    _create_circle(
                        _canvas_, drawposDead[0], drawposDead[1], 10, outline="#f11", fill="#f2ff00", width=1)
                    _canvas_.create_text(drawposDead[0] + 10, drawposDead[1], anchor=W, font="Arial",
                                         text=f'died\n{int(timediff)}s ago')
                if timediff > 5 and drawposDead != drawpos and SHOWGHOSTS:
                    _create_circle(
                        _canvas_, drawpos[0], drawpos[1], 10, outline="#f2ff00", fill="#000000", width=1)
            elif ANONYMOUS:
                if REVEALIMPOSTER and p.PlayerData.isImpostor:
                    _create_circle(
                        _canvas_, drawpos[0], drawpos[1], 10, outline="#f11", fill="#00FF00", width=1)
                else:
                    _create_circle(
                        _canvas_, drawpos[0], drawpos[1], 10, outline="#f11", fill=COLORS[7], width=1)
            else:
                _create_circle(
                    _canvas_, drawpos[0], drawpos[1], 10, outline="#f11", fill=COLORS[p.PlayerData.colorId], width=1)
                _canvas_.create_text(drawpos[0] + 10, drawpos[1], anchor=W, font="Arial",
                                     text=playerName)

        if GAME.localPlayer:
            for tpos in TASKPOS:
                drawpos = translateVec(tpos)
                _create_circle(
                    _canvas_, drawpos[0], drawpos[1], 4, outline="#f11", fill='#0f0', width=1)


def getDeadPlayer(p):
    global DEADPLAYERS
    for deadp in DEADPLAYERS:
        if p.Name == deadp.Name:
            return deadp


def manageDeadPlayer(p):
    global DEADPLAYERS
    found = False
    deadPlayer = None

    for deadp in DEADPLAYERS:
        if p.Name == deadp.Name and p.PlayerData.isDead:
            found = True
            deadPlayer = deadp
            break
        else:
            found = False

    if not found and p.PlayerData.isDead:
        p.killTimer = time.time()
        DEADPLAYERS.append(p)
    return found


def translateVecBack(event) -> StaticVector:
    map = MAPS[GAME.shipStatus.MapType] if GAME.shipStatus else None
    if map:
        scale = (map['image'].width(
        ) / map['size'][0], map['image'].height() / map['size'][1])

        center = map['center']
        x = (event.x - center[0]) / scale[0]
        y = (center[1] - event.y) / scale[1]
        return StaticVector(x, y)
    else:
        return StaticVector(0, 0)


def draw(_canvas_: Canvas):
    _canvas_.delete('all')
    global MAPS
    global TPTARGETPL
    try:
        drawmap(_canvas_)
    except Exception as e:
        pass

    _canvas_.update_idletasks()
    _canvas_.after(10, draw, (_canvas_))


def loadImage(path: str, scale: float) -> ImageTk.PhotoImage:
    image = Image.open(path)
    image = image.resize((int(image.width * scale), int(image.height * scale)))
    return ImageTk.PhotoImage(image)


def killmepls():
    global WINDOW
    WINDOW.destroy()
    os._exit(1)


def updateGraph():
    global WINDOW
    WINDOW = Tk()
    global MAPS

    def cbTpToClick(event):
        global CLICKTP
        if CLICKTP:
            pos = translateVecBack(event)
            if pos.X != 0 and pos.Y != 0 and GAME.localPlayer:
                GAME.setComponentPosition(GAME.localPlayer._addr, pos)

    MAPS[0]['image'] = loadImage('./map0.png', 0.5)
    MAPS[1]['image'] = loadImage('./map1.png', 0.5)
    MAPS[2]['image'] = loadImage('./map2.png', 0.5)
    canvas = Canvas(WINDOW)
    canvas.bind("<Button-1>", cbTpToClick)
    canvas.grid()
    canvas.config(bg='white')
    draw(canvas)
    WINDOW.lift()
    WINDOW.attributes('-topmost', True)
    WINDOW.attributes('-alpha', 0.6)
    WINDOW.wm_title('[amongthem] by Zat & itsEzz')
    WINDOW.protocol("WM_DELETE_WINDOW", killmepls)
    WINDOW.mainloop()


ZERO: StaticVector = StaticVector(0.0, 0.0)


def hackerino():
    global TPTARGETPL
    global ZERO
    global SPEED
    lastprint = time.time()

    def setSpeed(speed):
        global SPEEDHACK
        if GAME.gameOptions:
            GAME.gameOptions.Speed = speed
        SPEEDHACK = True if speed != 1.0 else False

    def cbCompleteTasks():
        if GAME.localPlayer and not GAME.localPlayer.PlayerData.isImpostor:
            _tasks = [
                _task for _task in GAME.localPlayer.Tasks if _task.taskStep != _task.MaxStep]
            for _task in _tasks:
                GAME.rpcCompleteTask(_task)

    def cbToggleImpostor():
        global IMPOSTER
        if GAME.localPlayer:
            if not GAME.localPlayer.PlayerData.isImpostor:
                GAME.localPlayer.PlayerData.isImpostor = 1
                IMPOSTER = True
            else:
                GAME.localPlayer.PlayerData.isImpostor = 0
                IMPOSTER = False

    def cbToggleNoClip():
        global NOCLIP
        _go = GAME.getGameObject(GAME.localPlayer._addr)
        _layer = GAME.getGameObjectLayer(_go)
        if _layer == 8:
            _layer = 14
            NOCLIP = True
        else:
            _layer = 8
            NOCLIP = False
        GAME.setGameObjectLayer(_go, _layer)

    def cbAnonymousMode():
        global ANONYMOUS
        ANONYMOUS = not ANONYMOUS

    def cbShowGhosts():
        global SHOWGHOSTS
        SHOWGHOSTS = not SHOWGHOSTS

    def cbClickTp(val):
        global CLICKTP
        CLICKTP = val

    def cbChangeSpeed():
        global SPEED
        SPEED = SPEED + 0.5 if SPEED <= 2.5 else 1.0

    def cbRevealImposter():
        global REVEALIMPOSTER
        REVEALIMPOSTER = not REVEALIMPOSTER

    def cbWalkPath():
        global WALKPATH
        WALKPATH = not WALKPATH

    def cbSHOWHOTKEYS():
        global SHOWHOTKEYS
        SHOWHOTKEYS = not SHOWHOTKEYS

    _speed = Hotkeys('shift',
                     lambda e: setSpeed(SPEED),
                     lambda e: setSpeed(1.0))
    _speed = Hotkeys('alt',
                     lambda e: cbToggleNoClip())
    _impostor = Hotkeys('f1',
                        lambda e: cbToggleImpostor())
    _completeTasks = Hotkeys('f2', lambda e: cbCompleteTasks())
    _anonMode = Hotkeys('f3', lambda e: cbAnonymousMode())
    _showGhosts = Hotkeys('f4', lambda e: cbShowGhosts())
    _speedVal = Hotkeys('plus', lambda e: cbChangeSpeed())
    _clickTp = Hotkeys('ctrl',
                       lambda e: cbClickTp(True),
                       lambda e: cbClickTp(False))
    _revealImposter = Hotkeys('f5', lambda e: cbRevealImposter())
    _walkPath = Hotkeys('f6', lambda e: cbWalkPath())
    _SHOWHOTKEYS = Hotkeys('f8', lambda e: cbSHOWHOTKEYS())

    while True:
        if not GAME.update():
            if GAME.initialized and not ctypes.windll.user32.FindWindowW(0, 'Among Us'):
                killmepls()
            time.sleep(1)
            continue

        if time.time() - lastprint > 1:
            # print('=' * 10)
            lastprint = time.time()

        time.sleep(0.01)


TASKPOS = []


def updateTaskPos():
    global TASKPOS

    while True:
        pos = []
        if GAME.localPlayer and GAME.shipStatus and GAME.shipRooms and GAME.allPlayers:
            for t in GAME.localPlayer.Tasks:
                if not t.HasLocation or t.taskStep >= t.MaxStep:
                    continue
                room = next(filter(lambda r: r.SystemType ==
                                   t.StartAt, GAME.shipRooms), None)
                if room:
                    pos.append(GAME.getComponentPosition(room._addr))
        TASKPOS = pos
        time.sleep(1.5)


def GetWindowRectFromName(name: str) -> tuple:
    hwnd = ctypes.windll.user32.FindWindowW(0, name)
    if not hwnd:
        return
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
    return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)


def main():
    _quit = Hotkeys('f10', lambda e: os.kill(os.getpid(), signal.SIGTERM))
    print("Initializing Game...")

    drawthread = Thread(None, updateGraph, 'draw')
    drawthread.start()

    while not GAME.initialized:
        print(' > Waiting for initalization; waiting for 5s...')
        time.sleep(5)

    print(f'GameAssembly.dll: {hex(GAME.gameAssemblyBase)}')
    print(f'UnityPlayer.dll: {hex(GAME.unityPlayerBase)}')
    hackThread = Thread(None, hackerino, 'hack')
    hackThread.start()
    posThread = Thread(None, updateTaskPos, 'taskPos')
    posThread.start()

    hackThread.join()
    drawthread.join()


if __name__ == '__main__':
    main()
