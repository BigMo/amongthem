import time
import random
from typing import Tuple
from PIL import ImageTk, Image

from threading import Thread
from game import GAME, StaticVector
from helpers import Hotkeys

from tkinter import Tk, Canvas, W, NW, SW


TPTARGET = 0

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
        'center': (124, 468),
        'size': (abs(-5 - 31), abs(-3.3 - 26.5))
    },
    2: {
        'image': None,
        'center': (-5, 0),
        'size': (abs(0.4 - 41), abs(-27 - 0))
    }
}

UI_TEXT = """Hotkeys:
[Shift] - Hold for Speedhack
[I] - Toggle Impostor on/off
"""


def currentTpTarget():
    return GAME.allPlayers[TPTARGET] if GAME.allPlayers and TPTARGET < len(GAME.allPlayers) else None


def drawmap(_canvas_: Canvas):
    global MAPS

    map = MAPS[GAME.shipStatus.MapType] if GAME.shipStatus else None

    if map:
        size = (map['image'].width(), map['image'].height())
        scale = (map['image'].width(
        ) / map['size'][0], map['image'].height() / map['size'][1])
        if _canvas_.winfo_width() != size[0] or _canvas_.winfo_height() != size[1]:
            _canvas_.config(width=size[0], height=size[1])

        center = map['center']

        def _create_circle(self, x, y, r, **kwargs):
            return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

        _canvas_.create_image(0, 0, image=map['image'], anchor=NW)

        _create_circle(_canvas_, center[0], center[1], 10, fill='#fff')

        for p in GAME.allPlayers:
            pos = p.NetworkTransform.TargetSyncPos if p.PlayerId != GAME.localPlayer.PlayerId else p.NetworkTransform.PrevPosSend

            drawpos = (center[0] + pos.X * scale[0],
                       (center[1] - pos.Y * scale[1]))
            _create_circle(
                _canvas_, drawpos[0], drawpos[1], 10, outline="#f11", fill=COLORS[p.PlayerData.colorId], width=1)
            _canvas_.create_text(drawpos[0] + 10, drawpos[1], anchor=W, font="Arial",
                                 text=f'{p.Name}\n{"DEAD" if p.PlayerData.isDead else ""}')


def draw(_canvas_: Canvas):
    _canvas_.delete('all')
    global MAPS
    global TPTARGET

    drawmap(_canvas_)

    _canvas_.create_text(5, 5, anchor=NW, font="Arial", text=UI_TEXT)

    _target = currentTpTarget()
    if _target:
        _canvas_.create_text(5, _canvas_.winfo_height() - 5, anchor=SW, font='Arial',
                             text=f'Current TP-Target: {_target.Name}')

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
    canvas = Canvas(root, bg='white')  # , width=SIZE[0], height=SIZE[1])
    canvas.grid()
    draw(canvas)
    root.lift()
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.6)
    # root.wm_attributes("-transparentcolor", "white")
    root.wm_title('[amongthem] by Zat')
    root.mainloop()


ZERO: StaticVector = StaticVector(0.0, 0.0)


def hackerino():
    global TPTARGET
    global ZERO
    lastprint = time.time()

    def cbTpTargetCountUp():
        global TPTARGET
        TPTARGET = (TPTARGET + 1) % len(GAME.allPlayers)

    def cbTpToTarget():
        _target = currentTpTarget()
        if _target and GAME.localPlayer:
            _pos = GAME.getComponentPosition(_target._addr)
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

    def getPosition():
        # pTransform = GAME.getTransform(GAME.localPlayer)
        # pos = GAME.getTransformPosition(pTransform)
        pos = GAME.getComponentPosition(GAME.localPlayer._addr)
        print(f'X: {round(pos.X,2)}, Y: {round(pos.Y,2)}')

    def setPosition():
        # pTransform = GAME.getTransform(GAME.localPlayer)
        newPos: StaticVector = StaticVector(0.0, 0.0)
        # pos = GAME.getTransformPosition(pTransform)
        pos = GAME.getComponentPosition(GAME.localPlayer._addr)
        print(f'X: {round(pos.X,2)}, Y: {round(pos.Y,2)}')

        GAME.setComponentPosition(GAME.localPlayer._addr, newPos)
        # GAME.setTransformPosition(pTransform, newPos)

        pos = GAME.getComponentPosition(GAME.localPlayer._addr)
        # pos = GAME.getTransformPosition(pTransform)
        print(f'X: {round(pos.X,2)}, Y: {round(pos.Y,2)}')

    def cbRandomizePlayer():
        GAME.rpcSetHat(int(random.randrange(0, 93)))
        GAME.rpcSetPet(int(random.randrange(0, 10)))
        GAME.rpcSetSkin(int(random.randrange(0, 10)))

    def cbTestLayer():
        _go = GAME.getGameObject(GAME.localPlayer._addr)
        print(f' > Gameobject of {hex(GAME.localPlayer._addr)} at {hex(_go)}!')
        _layer = GAME.getGameObjectLayer(_go)
        print(f' > Layer of {hex(_go)}: {_layer}!')
        # _layer = 14 if _layer == 8 else 8
        # print(f' > Set layer to {_layer}...')
        # GAME.setGameObjectLayer(_go, _layer)
        # _layer = GAME.getGameObjectLayer(_go)
        # print(f' > Layer of {hex(_go)}: {_layer}!')

    def cbTestRevive():
        print(f'Attempting revive...')
        GAME.revive(GAME.localPlayer._addr)

    _speed = Hotkeys('shift',
                     lambda e: setSpeed(3.0),
                     lambda e: setSpeed(1.0))
    _impostor = Hotkeys('insert',
                        lambda e: cbToggleImpostor())
    _targetUp = Hotkeys('plus', lambda e: cbTpTargetCountUp())
    _tpToTarget = Hotkeys('delete', lambda e: cbTpToTarget())
    _completeTasks = Hotkeys('home', lambda e: cbCompleteTasks())
    # _randomHat = Hotkeys('f1', lambda e: cbRandomizePlayer())
    _test = Hotkeys('f1', lambda e: cbTestLayer())
    _test2 = Hotkeys('f2', lambda e: cbTestRevive())

    while True:
        if not GAME.update():
            time.sleep(1)
            continue

        if time.time() - lastprint > 1:
            # print('=' * 10)
            lastprint = time.time()

        time.sleep(0.01)


def main():
    print("Initializing Game...")

    while not GAME.initialized:
        print(' > Waiting for initalization; waiting for 5s...')
        time.sleep(5)

    print(f'GameAssembly.dll: {hex(GAME.gameAssemblyBase)}')
    print(f'UnityPlayer.dll: {hex(GAME.unityPlayerBase)}')

    drawthread = Thread(None, updateGraph, 'draw')
    drawthread.start()
    hackThread = Thread(None, hackerino, 'hack')
    hackThread.start()

    hackThread.join()
    drawthread.join()


if __name__ == '__main__':
    main()
