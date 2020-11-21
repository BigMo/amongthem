import time
import os
import signal
import random
from typing import Tuple
from PIL import ImageTk, Image
from threading import Thread
from tkinter import Tk, Canvas, W, NW, SW, SE, NE

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

DEADPLAYERS = []

UI_TEXT = """Hotkeys:
[Shift] - Hold for Speedhack
[F1] - Impostor on/off
[Alt] - Noclip on/off
[F2] - Select TP Target
[F3] - TP to target
[F4] - Select TP room
[F5] - TP to room
[F6] - Complete all tasks
[F7] - Anonymous Mode on/off
[F8] - Show Ghosts on/off
[F11] - Quit
"""


def currentTpTarget():
    return GAME.allPlayers[TPTARGETPL] if GAME.allPlayers and TPTARGETPL < len(GAME.allPlayers) else None


def currentTpTargetRoom() -> IPlainRoom:
    return GAME.shipRooms[TPTARGETRO] if GAME.shipRooms and TPTARGETRO < len(GAME.shipRooms) else None


def drawmap(_canvas_: Canvas):
    global MAPS
    global ANONYMOUS
    global DEADPLAYERS
    global SHOWGHOSTS

    map = MAPS[GAME.shipStatus.MapType] if GAME.shipStatus else None

    if map:
        size = (map['image'].width(), map['image'].height())
        scale = (map['image'].width(
        ) / map['size'][0], map['image'].height() / map['size'][1])
        if _canvas_.winfo_width() != size[0] or _canvas_.winfo_height() != size[1]:
            _canvas_.config(width=size[0], height=size[1]+220)

        center = map['center']

        def _create_circle(self, x, y, r, **kwargs):
            return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

        _canvas_.create_image(0, 0, image=map['image'], anchor=NW)

        def translateVec(vec) -> Tuple[float, float]:
            return (center[0] + vec.X * scale[0],
                    (center[1] - vec.Y * scale[1]))

        if not ANONYMOUS:
            for p in [p for p in GAME.allPlayers if not p.PlayerData.isDead]:
                _his = GAME.playerPositions.get(p.PlayerId)
                if _his and len(_his.items) > 1:
                    dpts = [translateVec(p) for p in _his.items]
                    pts = [p for v in dpts for p in v]
                    _canvas_.create_line(
                        *pts, fill="#f11", width=3, smooth=True)
                    _canvas_.create_line(
                        *pts, fill=COLORS[p.PlayerData.colorId], smooth=True)
        if len(GAME.allPlayers) == 0:
            DEADPLAYERS.clear()
        for p in GAME.allPlayers:
            deadPlayer = manageDeadPlayer(p)
            drawposDead = None
            deadPlayerObj = None
            pos = p.NetworkTransform.TargetSyncPos if p.PlayerId != GAME.localPlayer.PlayerId else p.NetworkTransform.PrevPosSend
            if deadPlayer:
                deadPlayerObj = getDeadPlayer(p)
                drawposDead = translateVec(deadPlayerObj.NetworkTransform.TargetSyncPos)

            drawpos = translateVec(pos)

            if deadPlayer:
                timediff = time.time() - deadPlayerObj.killTimer
                if timediff < 40:
                    _create_circle(
                        _canvas_, drawposDead[0], drawposDead[1], 10, outline="#f11", fill="#f2ff00", width=1)
                    _canvas_.create_text(drawposDead[0] + 10, drawposDead[1], anchor=W, font="Arial",
                                        text=f'KILLED\n{int(timediff)}s ago')
                if timediff > 5 and drawposDead != drawpos and SHOWGHOSTS:
                    _create_circle(
                        _canvas_, drawpos[0], drawpos[1], 10, outline="#f11", fill="#000000", width=1)
                    _canvas_.create_text(drawpos[0] + 10, drawpos[1], anchor=W, font="Arial",
                                     text='GHOST')
            elif ANONYMOUS:
                _create_circle(
                    _canvas_, drawpos[0], drawpos[1], 10, outline="#f11", fill=COLORS[7], width=1)
            else:
                _create_circle(
                    _canvas_, drawpos[0], drawpos[1], 10, outline="#f11", fill=COLORS[p.PlayerData.colorId], width=1)
                _canvas_.create_text(drawpos[0] + 10, drawpos[1], anchor=W, font="Arial",
                                     text=f'{p.Name}\n{"DEAD" if p.PlayerData.isDead else ""}')


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


def draw(_canvas_: Canvas):
    _canvas_.delete('all')
    global MAPS
    global TPTARGETPL

    drawmap(_canvas_)

    _canvas_.create_text(5, _canvas_.winfo_height() - 220,
                         anchor=NW, font="Arial", text=UI_TEXT)

    _targetPlayer = currentTpTarget()
    _targetRoom = currentTpTargetRoom()
    _tpTargets = 'Targets:\n'
    if _targetPlayer:
        _tpTargets += f'TP-Target: {_targetPlayer.Name}\n'

    if _targetRoom:
        _tpTargets += f'TP-Target-Room: {DATA["CONSTS"]["SYSTEM_TYPES"][_targetRoom.SystemType]}'

    _canvas_.create_text(_canvas_.winfo_width() - 5, _canvas_.winfo_height() - 200, anchor=NE, font='Arial',
                         text=_tpTargets)

    _canvas_.update_idletasks()
    _canvas_.after(10, draw, (_canvas_))


def loadImage(path: str, scale: float) -> ImageTk.PhotoImage:
    image = Image.open(path)
    image = image.resize((int(image.width * scale), int(image.height * scale)))
    return ImageTk.PhotoImage(image)


def updateGraph():
    root = Tk()
    global MAPS
    MAPS[0]['image'] = loadImage('./map0.png', 0.5)
    MAPS[1]['image'] = loadImage('./map1.png', 0.5)
    MAPS[2]['image'] = loadImage('./map2.png', 0.5)
    canvas = Canvas(root)  # , width=SIZE[0], height=SIZE[1])
    canvas.grid()
    canvas.config(bg='white')
    draw(canvas)
    root.lift()
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.6)
    # root.wm_attributes("-transparentcolor", "white")
    root.wm_title('[amongthem] by Zat & itsEzz')
    root.mainloop()


ZERO: StaticVector = StaticVector(0.0, 0.0)


def hackerino():
    global TPTARGETPL
    global ZERO
    lastprint = time.time()

    def cbTpTargetCountUp():
        global TPTARGETPL
        TPTARGETPL = (TPTARGETPL + 1) % len(GAME.allPlayers)

    def cbTpTargetRoomCountUp():
        global TPTARGETRO
        TPTARGETRO = (TPTARGETRO + 1) % len(GAME.shipRooms)

    def cbTpToTarget():
        _target = currentTpTarget()
        if _target and GAME.localPlayer:
            _pos = GAME.getComponentPosition(_target._addr)
            GAME.setComponentPosition(GAME.localPlayer._addr, _pos)

    def cbTpToTargetRoom():
        _target = currentTpTargetRoom()
        if _target and GAME.localPlayer:
            _pos = GAME.getComponentPosition(_target.pRoomArea)
            GAME.setComponentPosition(GAME.localPlayer._addr, _pos)

    def setSpeed(speed):
        if GAME.gameOptions:
            GAME.gameOptions.Speed = speed

    def cbCompleteTasks():
        if GAME.localPlayer and not GAME.localPlayer.PlayerData.isImpostor:
            _tasks = [
                _task for _task in GAME.localPlayer.Tasks if _task.taskStep != _task.MaxStep]
            for _task in _tasks:
                GAME.rpcCompleteTask(_task)

    def cbToggleImpostor():
        if GAME.localPlayer:
            GAME.localPlayer.PlayerData.isImpostor = 1 if not GAME.localPlayer.PlayerData.isImpostor else 0

    def cbRandomizePlayer():
        GAME.rpcSetHat(int(random.randrange(0, 93)))
        GAME.rpcSetPet(int(random.randrange(0, 10)))
        GAME.rpcSetSkin(int(random.randrange(0, 10)))

    def cbToggleNoClip():
        _go = GAME.getGameObject(GAME.localPlayer._addr)
        _layer = GAME.getGameObjectLayer(_go)
        _layer = 14 if _layer == 8 else 8
        GAME.setGameObjectLayer(_go, _layer)

    def cbAnonymousMode():
        global ANONYMOUS
        ANONYMOUS = not ANONYMOUS

    def cbShowGhosts():
        global SHOWGHOSTS
        SHOWGHOSTS = not SHOWGHOSTS

    _speed = Hotkeys('shift',
                     lambda e: setSpeed(3.0),
                     lambda e: setSpeed(1.0))
    _speed = Hotkeys('alt',
                     lambda e: cbToggleNoClip())
    _impostor = Hotkeys('f1',
                        lambda e: cbToggleImpostor())
    _targetUp = Hotkeys('f2', lambda e: cbTpTargetCountUp())
    _tpToTarget = Hotkeys('f3', lambda e: cbTpToTarget())

    _targetUpRo = Hotkeys('f4', lambda e: cbTpTargetRoomCountUp())
    _tpToTargetRo = Hotkeys('f5', lambda e: cbTpToTargetRoom())

    _completeTasks = Hotkeys('f6', lambda e: cbCompleteTasks())
    # _randomHat = Hotkeys('f1', lambda e: cbRandomizePlayer())
    _anonMode = Hotkeys('f7', lambda e: cbAnonymousMode())
    #_test = Hotkeys('f1', lambda e: cbRandomizePlayer())
    _showGhosts = Hotkeys('f8', lambda e: cbShowGhosts())

    while True:
        if not GAME.update():
            time.sleep(1)
            continue

        if time.time() - lastprint > 1:
            # print('=' * 10)
            lastprint = time.time()

        time.sleep(0.01)


def main():
    _quit = Hotkeys('f11', lambda e: os.kill(os.getpid(), signal.SIGTERM))
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

    hackThread.join()
    drawthread.join()


if __name__ == '__main__':
    main()
