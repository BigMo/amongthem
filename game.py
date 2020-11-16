import struct
from struct import unpack
import x86
from reclassparser import _TYPES
from typing import Any, Dict, List, Sequence, TypeVar, cast
import pymem
from pymem import Pymem
from helpers import PointerChain
from x86 import ShellCode, ShellCodeInjector

pPlayerControlStatic = PointerChain([0x144bb70, 0x5c, 0])
pShipStatusStatic = PointerChain([0x144BB58, 0x5c, 0, 0])
pGameOptions = PointerChain([0x0144BB70, 0x5c, 4, 0])
pLocalPos = PointerChain([0x01277F00, 0x20, 0x34, 0x4, 0x40, 0])

DATA = {
    'OFFSETS': {

    },
    'STRUCTS': {
        'PlayerControlStatic': {
            "pAllPlayerControls": {
                "offset": 8,
                "unpack": "I"
            },
            "pGameOptions": {
                "offset": 4,
                "unpack": "I"
            },
            "pLocalPlayer": {
                "offset": 0,
                "unpack": "I"
            }
        },
        'PlayerControl': {
            "Klass": {
                "offset": 0,
                "unpack": "i"
            },
            "MaxReportDistance": {
                "offset": 44,
                "unpack": "f"
            },
            "pNetworkTransform": {
                "offset": 96,
                "unpack": "i"
            },
            "pPlayerData": {
                "offset": 52,
                "unpack": "i"
            },
            "PlayerId": {
                "offset": 40,
                "unpack": "i"
            },
            "RemainingEmergencies": {
                "offset": 72,
                "unpack": "i"
            },
            "inVent": {
                "offset": 49,
                "unpack": "?"
            },
            "killTimer": {
                "offset": 68,
                "unpack": "f"
            },
            "moveable": {
                "offset": 48,
                "unpack": "?"
            },
            "pMyTasks": {
                "offset": 116,
                "unpack": "i"
            }
        },
        'PlayerData': {
            "colorId": {
                "offset": 16,
                "unpack": "b"
            },
            "isDead": {
                "offset": 41,
                "unpack": "?"
            },
            "isImpostor": {
                "offset": 40,
                "unpack": "?"
            },
            "pName": {
                "offset": 12,
                "unpack": "i"
            },
            "pPlayerControls": {
                "offset": 44,
                "unpack": "i"
            },
            "playerId": {
                "offset": 8,
                "unpack": "i"
            }
        },
        'List': {
            'pArray': {
                'offset': 8,
                'unpack': 'i'
            },
            'size': {
                'offset': 12,
                'unpack': 'i'
            }
        },
        'Array': {
            'max_length': {
                'offset': 12,
                'unpack': 'i'
            },
            'pItems': {
                'offset': 16,
                'unpack': 'i'
            }
        },
        'String': {
            "chars": {
                "offset": 12,
                "unpack": "i"
            },
            "length": {
                "offset": 8,
                "unpack": "i"
            }
        },
        'CustomNetworkTransform': {
            "LastSequenceId": {
                "offset": 76,
                "unpack": "i"
            },
            "PrevPosSend": {
                "offset": 80,
                "type": "Vector2"
            },
            "PrevVelSend": {
                "offset": 88,
                "type": "Vector2"
            },
            "TargetSyncPos": {
                "offset": 60,
                "type": "Vector2"
            },
            "TargetSyncVel": {
                "offset": 68,
                "type": "Vector2"
            }
        },
        'Vector2': {
            'X': {
                'offset': 0,
                'unpack': 'f'
            },
            'Y': {
                'offset': 4,
                'unpack': 'f'
            }
        },
        'ShipStatus': {
            "EmergencyCooldown": {
                "offset": 208,
                "unpack": "f"
            },
            "InitialSpawnCenter": {
                "offset": 72,
                "type": "Vector2"
            },
            "MapScale": {
                "offset": 60,
                "unpack": "f"
            },
            "MapType": {
                "offset": 212,
                "unpack": "i"
            },
            "MeetingSpawnCenter": {
                "offset": 80,
                "type": "Vector2"
            },
            "MeetingSpawnCenter2": {
                "offset": 88,
                "type": "Vector2"
            },
            "Timer": {
                "offset": 204,
                "unpack": "f"
            }
        },
        'GameOptions': {
            "Speed": {
                "offset": 20,
                "unpack": "f"
            },
        },
        'LocalPos': {
            "Pos": {
                "offset": 236,
                "type": "Vector2"
            }
        },
        'Task': {
            "HasLocation": {
                "offset": 36,
                "unpack": "?"
            },
            "LocationDirty": {
                "offset": 37,
                "unpack": "?"
            },
            "MaxStep": {
                "offset": 44,
                "unpack": "i"
            },
            "TaskId": {
                "offset": 16,
                "unpack": "i"
            },
            "ShowTaskStep": {
                "offset": 48,
                "unpack": "?"
            },
            "ShowTaskTimer": {
                "offset": 49,
                "unpack": "?"
            },
            "StartAt": {
                "offset": 24,
                "unpack": "i"
            },
            "TaskTimer": {
                "offset": 56,
                "unpack": "f"
            },
            "TaskType": {
                "offset": 28,
                "unpack": "i"
            },
            "TimerStarted": {
                "offset": 52,
                "unpack": "i"
            },
            "taskStep": {
                "offset": 40,
                "unpack": "i"
            }
        }
    }
}

CALL_RPC_COMPLETE_TASK_PAYLOAD: bytes = bytes(
    [0x6A, 0x00, 0x6A, 0x00, 0x68, 0x00, 0x00, 0x00, 0x00, 0xE8, 0x00, 0x00, 0x00, 0x00])
RPC_COMPLETE_TASK_OFFSET = 0x622A70
RPC_SET_HAT = 0x622F60
RPC_SET_PET = 0x6231F0
RPC_SET_SKIN = 0x623380
SET_COLOR = 0x6236D0
COMPONENT_GET_TRANSFORM = 0x464A10
COMPONENT_GET_GAMEOBJECT = 0x464980
TRANSFORM_GET_POSITION = 0x4477D0
TRANFORM_SET_POSITION = 0x447C80
GAMEOBJECT_GET_LAYER = 0x466E00
GAMEOBJECT_SET_LAYER = 0x466E90
PLAYERCONTROL_REVIVE = 0x622880
LAYER_PLAYER = 8
LAYER_GHOST = 14


def calcTypeSize(_type: Dict[str, Any]) -> int:
    size = 0

    highestField = next(
        iter(sorted(_type.items(), key=lambda i: i[1]['offset'], reverse=True)), None)
    if not highestField:
        raise Exception('No field found!')

    data = highestField[1]
    _type = data.get('unpack')
    if _type:
        return data.get('offset') + 8
    else:
        _type = data.get('type')
        if not _type:
            raise Exception('Neither unpack nor type found!')
        _type = DATA['STRUCTS'].get(_type)
        if not _type:
            raise Exception(f'Type \"{_type}\" not found!')
        return data.get('offset') + calcTypeSize(_type)


def getTypeSize(_type: Dict[str, Any]) -> int:
    size = _type.get('_size')
    if size != None:
        return size
    else:
        size = calcTypeSize(_type)
        _type['_size'] = size
        return size


class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'},
            last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        _current = self.get(key)
        self.__setitem__(key, value)
        if isinstance(value, dict):
            return

        if _current == value:
            return

        _pm: Pymem = self.get('_pm')
        _type = self.get('_type')
        _addr = self.get('_addr')
        _bytes = struct.pack(_type[key]['unpack'], value)
        _pm.write_bytes(_addr + _type[key]['offset'], _bytes, len(_bytes))

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


def unpackType(pm: Pymem, rawdata: bytes, addr: 0, baseOffset: 0, _type: Dict[str, Any]):
    ret = Map()
    ret['_type'] = _type
    ret['_pm'] = pm
    ret['_addr'] = addr + baseOffset

    for name, meta in _type.items():  # for each field:
        if name.startswith('_'):
            continue
        ret[name] = None
        _unpack = meta.get('unpack')
        _offset = meta.get('offset')
        if _unpack:  # primitive type: unpack raw bytes
            start = baseOffset + _offset
            end = baseOffset + _offset + struct.calcsize(_unpack)
            ret[name] = struct.unpack(_unpack, rawdata[start: end])[0]
        else:  # type
            _fieldType = meta.get('type')
            if not _fieldType:
                raise Exception('Neither type nor offset!')
            _type = DATA['STRUCTS'].get(_fieldType)
            if not _type:
                raise Exception(f'Unknown type \"{_fieldType}\"')
            ret[name] = unpackType(
                pm, rawdata, addr, baseOffset + _offset, _type)

    return ret


def readType(pm: Pymem, addr: int, _type: Dict[str, Any]):
    # try:
    rawdata = pm.read_bytes(addr, getTypeSize(_type))  # read raw bytes
    return unpackType(pm, rawdata, addr, 0, _type)
    # except:
    #    return None


class IVector2:
    @property
    def X(self) -> float:
        pass

    @property
    def Y(self) -> float:
        pass


class ICustomNetworkTransform:
    @property
    def TargetSyncPos(self) -> IVector2:
        pass

    @property
    def TargetSyncVel(self) -> IVector2:
        pass

    @property
    def LastSequenceId(self) -> int:
        pass

    @property
    def PrevPosSend(self) -> IVector2:
        pass

    @property
    def PrevVelSend(self) -> IVector2:
        pass


class IPlayerControlStatic:
    @property
    def pLocalPlayer(self) -> int:
        pass

    @property
    def pGameOptions(self) -> int:
        pass

    @property
    def pAllPlayerControls(self) -> int:
        pass


class IList:
    @property
    def pArray(self) -> int:
        pass

    @property
    def size(self) -> int:
        pass


class IArray:
    @property
    def max_length(self) -> int:
        pass

    @property
    def pItems(self) -> int:
        pass


class IString:
    @property
    def length(self) -> int:
        pass

    @property
    def chars(self) -> int:
        pass


class IPlayerControl:
    @property
    def Klass(self) -> int:
        pass

    @property
    def BNHPKAJEEKJ(self) -> int:
        pass

    @property
    def PlayerId(self) -> int:
        pass

    @property
    def MaxReportDistance(self) -> float:
        pass

    @property
    def moveable(self) -> bool:
        pass

    @property
    def inVent(self) -> bool:
        pass

    @property
    def pPlayerData(self) -> int:
        pass

    @property
    def killTimer(self) -> float:
        pass

    @property
    def RemainingEmergencies(self) -> int:
        pass

    @property
    def pNetworkTransform(self) -> int:
        pass

    @property
    def pMyTasks(self) -> int:
        pass


class IPlayerData:
    @property
    def playerId(self) -> int:
        pass

    @property
    def pName(self) -> int:
        pass

    @property
    def colorId(self) -> int:
        pass

    @property
    def isImpostor(self) -> bool:
        pass

    @property
    def isDead(self) -> bool:
        pass

    @property
    def pPlayerControls(self) -> int:
        pass


class ITask:
    @property
    def StartAt(self) -> int:
        pass

    @property
    def TaskType(self) -> int:
        pass

    @property
    def TaskId(self) -> int:
        pass

    @property
    def HasLocation(self) -> bool:
        pass

    @property
    def LocationDirty(self) -> bool:
        pass

    @property
    def taskStep(self) -> int:
        pass

    @property
    def MaxStep(self) -> int:
        pass

    @property
    def ShowTaskStep(self) -> bool:
        pass

    @property
    def ShowTaskTimer(self) -> bool:
        pass

    @property
    def TimerStarted(self) -> int:
        pass

    @property
    def TaskTimer(self) -> float:
        pass


class IFullPlayerControl(IPlayerControl):
    @property
    def Name(self) -> str:
        pass

    @property
    def PlayerData(self) -> IPlayerData:
        pass

    @property
    def NetworkTransform(self) -> ICustomNetworkTransform:
        pass

    @property
    def Tasks(self) -> Sequence[ITask]:
        pass


class IShipStatus:
    @property
    def MapScale(self) -> float:
        pass

    @property
    def InitialSpawnCenter(self) -> IVector2:
        pass

    @property
    def MeetingSpawnCenter(self) -> IVector2:
        pass

    @property
    def MeetingSpawnCenter2(self) -> IVector2:
        pass

    @property
    def Timer(self) -> float:
        pass

    @property
    def EmergencyCooldown(self) -> float:
        pass

    @property
    def MapType(self) -> int:
        pass


class IGameOptions:
    @property
    def Speed(self) -> float:
        pass


class ILocalPos:
    @property
    def Pos(self) -> IVector2:
        pass


class StaticVector:
    def __init__(self, x, y):
        self._x_ = x
        self._y_ = y

    @ property
    def X(self) -> float:
        return self._x_

    @ property
    def Y(self) -> float:
        return self._y_


fn_GameObject_get_layer: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('pGameObject')\
    .movInt32ToEaxOperand('pGameObjectGetLayer')\
    .callEax()\
    .addInt8ToEsp(0x8)\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 4)

fn_Component_get_GameObject: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('pComponent')\
    .movInt32ToEaxOperand('pComponentGetGameObject')\
    .callEax()\
    .addInt8ToEsp(0x8)\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 4)


class Game:
    def __init__(self):
        self._pm_: Pymem = None
        self._gameAssemblyBase_: int = 0
        self._unityPlayerBase_: int = 0
        self._gameOptions_: IGameOptions = None
        self._shipStatus_: IShipStatus = None
        self._playerControlStatic_: IPlayerControlStatic = None
        self._localPlayer_: IFullPlayerControl = None
        self._allPlayers_: Sequence[IFullPlayerControl] = []
        self._injector_: ShellCodeInjector = None

    @property
    def pm(self) -> Pymem:
        return self._pm_

    @property
    def gameAssemblyBase(self) -> int:
        return self._gameAssemblyBase_

    @property
    def unityPlayerBase(self) -> int:
        return self._unityPlayerBase_

    @property
    def gameOptions(self) -> IGameOptions:
        return self._gameOptions_

    @property
    def shipStatus(self) -> IShipStatus:
        return self._shipStatus_

    @property
    def playerControlStatic(self) -> IPlayerControlStatic:
        return self._playerControlStatic_

    @property
    def localPlayer(self) -> IFullPlayerControl:
        return self._localPlayer_

    @property
    def allPlayers(self) -> Sequence[IFullPlayerControl]:
        return self._allPlayers_

    @property
    def initialized(self) -> bool:
        if self._pm_ == None:
            try:
                self._pm_ = Pymem('Among Us.exe')
                self._injector_ = ShellCodeInjector(self._pm_)
            except:
                return False
        if self._gameAssemblyBase_ == 0:
            try:
                self._gameAssemblyBase_ = pymem.process.module_from_name(
                    self._pm_.process_handle, 'GameAssembly.dll').lpBaseOfDll
            except:
                return False
        if self._unityPlayerBase_ == 0:
            try:
                self._unityPlayerBase_ = pymem.process.module_from_name(
                    self._pm_.process_handle, 'UnityPlayer.dll').lpBaseOfDll
            except:
                return False
        return True

    def update(self) -> bool:
        if not self.initialized:
            return False

        try:
            self._playerControlStatic_ = self._getPlayerControlStatic_()
            # Local player
            _local = self._getPlayerControl_(
                self._playerControlStatic_.pLocalPlayer)
            self._localPlayer_ = self._getFullPlayer_(_local)
            # All players
            _allPlayers = self._getList_(
                self._playerControlStatic_.pAllPlayerControls, DATA['STRUCTS']['PlayerControl'])
            self._allPlayers_ = [self._getFullPlayer_(
                player) for player in _allPlayers]
            # GameOptions
            self._gameOptions_ = self._getGameOptions_()
            # ShipStatus
            self._shipStatus_ = self._getShipStatus_()
        except:
            return False

        return True

    def setColor(self, colorId: int) -> None:
        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt8(colorId)\
            .pushInt32(self._localPlayer_._addr)\
            .movInt32ToEax(self._gameAssemblyBase_ + SET_COLOR)\
            .callEax()\
            .addInt8ToEsp(0x0c)\
            .ret()\
            .assemble()
        print(' '.join([format(i, 'x') for i in code]))
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

    def rpcSetHat(self, hatId: int) -> None:
        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt8(hatId)\
            .pushInt32(self._localPlayer_._addr)\
            .movInt32ToEax(self._gameAssemblyBase_ + RPC_SET_HAT)\
            .callEax()\
            .addInt8ToEsp(0x0c)\
            .ret()\
            .assemble()
        print(' '.join([format(i, 'x') for i in code]))
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

    # def revive(self, pPlayer: int) -> None:
    #     code = x86.Assembler()\
    #         .pushInt8(0)\
    #         .pushInt32(pPlayer)\
    #         .movInt32ToEax(self._gameAssemblyBase_ + PLAYERCONTROL_REVIVE)\
    #         .callEax()\
    #         .addInt8ToEsp(0x08)\
    #         .ret()\
    #         .assemble()
    #     ShellcodeInjector.execute(self._pm_.process_handle, code)

    def rpcSetPet(self, petId: int) -> None:
        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt8(petId)\
            .pushInt32(self._localPlayer_._addr)\
            .movInt32ToEax(self._gameAssemblyBase_ + RPC_SET_PET)\
            .callEax()\
            .addInt8ToEsp(0x0c)\
            .ret()\
            .assemble()
        print(' '.join([format(i, 'x') for i in code]))
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

    def rpcSetSkin(self, skinId: int) -> None:
        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt8(skinId)\
            .pushInt32(self._localPlayer_._addr)\
            .movInt32ToEax(self._gameAssemblyBase_ + RPC_SET_SKIN)\
            .callEax()\
            .addInt8ToEsp(0x0c)\
            .ret()\
            .assemble()
        print(' '.join([format(i, 'x') for i in code]))
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

    def rpcCompleteTask(self, task: ITask) -> None:
        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt8(task.TaskId)\
            .pushInt32(self._localPlayer_._addr)\
            .movInt32ToEax(self._gameAssemblyBase_ + RPC_COMPLETE_TASK_OFFSET)\
            .callEax()\
            .addInt8ToEsp(0x0c)\
            .ret()\
            .assemble()
        print(' '.join([format(i, 'x') for i in code]))
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

    def getComponentPosition(self, pComponent: int) -> StaticVector:
        _resAddr = ShellCodeInjector.alloc(self._pm_.process_handle, 12)

        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt32(pComponent)\
            .movInt32ToEax(self._gameAssemblyBase_ + COMPONENT_GET_TRANSFORM)\
            .callEax()\
            .addInt8ToEsp(0x8)\
            .pushInt8(0)\
            .pushEax()\
            .pushInt32(_resAddr)\
            .movInt32ToEax(self._gameAssemblyBase_ + TRANSFORM_GET_POSITION)\
            .callEax()\
            .addInt8ToEsp(0xC)\
            .ret()\
            .assemble()
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)
        vec: IVector2 = readType(
            self._pm_, _resAddr, DATA['STRUCTS']['Vector2'])
        result = StaticVector(vec.X, vec.Y)

        ShellCodeInjector.free(self._pm_.process_handle, _resAddr, 12)
        return result

    def setComponentPosition(self, pComponent: int, pos: StaticVector):
        _buffer = ShellCodeInjector.alloc(self._pm_.process_handle, 12)
        self._pm_.write_float(_buffer, pos.X)
        self._pm_.write_float(_buffer + 4, pos.Y)

        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt32(pComponent)\
            .movInt32ToEax(self._gameAssemblyBase_ + COMPONENT_GET_TRANSFORM)\
            .callEax()\
            .addInt8ToEsp(0x8)\
            .movqQwordPtrInt32ToXmm0(_buffer)\
            .pushInt8(0)\
            .subInt8FromEsp(0xC)\
            .movEspToEcx()\
            .pushEax()\
            .movqXmm0ToQwordPtrEcx()\
            .movEsiToDwordPtrEcx8()\
            .movInt32ToEax(self._gameAssemblyBase_+TRANFORM_SET_POSITION)\
            .callEax()\
            .addInt8ToEsp(0x14)\
            .ret()\
            .assemble()
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

        ShellCodeInjector.free(self._pm_.process_handle, _buffer, 4)

    def getTransform(self, pComponent: int) -> int:
        _resAddr = ShellCodeInjector.alloc(self._pm_.process_handle, 4)

        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt32(pComponent)\
            .movInt32ToEax(self._gameAssemblyBase_ + COMPONENT_GET_TRANSFORM)\
            .callEax()\
            .addInt8ToEsp(0x8)\
            .movEaxToAddr(_resAddr)\
            .ret()\
            .assemble()
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

        result = self._pm_.read_int(_resAddr)
        ShellCodeInjector.free(self._pm_.process_handle, _resAddr, 4)
        return result

    def getGameObject(self, pComponent: int) -> int:
        global fn_Component_get_GameObject
        self._injector_.call(fn_Component_get_GameObject, {
            'pComponent': pComponent,
            'pComponentGetGameObject': self._gameAssemblyBase_ + COMPONENT_GET_GAMEOBJECT
        })
        return self._pm_.read_int(fn_Component_get_GameObject.buffers['pTargetBuffer'].addr)

    def getGameObjectLayer(self, pGameObject: int) -> int:
        global fn_GameObject_get_layer
        self._injector_.call(fn_GameObject_get_layer, {
            'pGameObject': pGameObject,
            'pGameObjectGetLayer': self._gameAssemblyBase_ + GAMEOBJECT_GET_LAYER
        })
        return self._pm_.read_int(fn_GameObject_get_layer.buffers['pTargetBuffer'].addr)

    def setGameObjectLayer(self, pGameObject: int, layer: int) -> None:
        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt32(layer)\
            .pushInt32(pGameObject)\
            .movInt32ToEax(self._gameAssemblyBase_ + GAMEOBJECT_SET_LAYER)\
            .callEax()\
            .addInt8ToEsp(0xC)\
            .ret()\
            .assemble()
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

    def getTransformPosition(self, pTransform: int) -> IVector2:
        _resAddr = ShellCodeInjector.alloc(self._pm_.process_handle, 12)

        code = x86.Assembler()\
            .pushInt8(0)\
            .pushInt32(pTransform)\
            .pushInt32(_resAddr)\
            .movInt32ToEax(self._gameAssemblyBase_ + TRANSFORM_GET_POSITION)\
            .callEax()\
            .addInt8ToEsp(0xC)\
            .ret()\
            .assemble()
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)
        result = readType(self._pm_, _resAddr, DATA['STRUCTS']['Vector2'])

        ShellCodeInjector.free(self._pm_.process_handle, _resAddr, 4)
        return result

    def setTransformPosition(self, pTransform: int, pos: IVector2):
        _buffer = ShellCodeInjector.alloc(self._pm_.process_handle, 12)
        self._pm_.write_float(_buffer, pos.X)
        self._pm_.write_float(_buffer + 4, pos.Y)

        code = x86.Assembler()\
            .movqQwordPtrInt32ToXmm0(_buffer)\
            .pushInt8(0)\
            .subInt8FromEsp(0xC)\
            .movEspToEcx()\
            .pushInt32(pTransform)\
            .movqXmm0ToQwordPtrEcx()\
            .movEsiToDwordPtrEcx8()\
            .movInt32ToEax(self._gameAssemblyBase_+TRANFORM_SET_POSITION)\
            .callEax()\
            .addInt8ToEsp(0x14)\
            .ret()\
            .assemble()
        ShellCodeInjector.executeOld(self._pm_.process_handle, code)

        ShellCodeInjector.free(self._pm_.process_handle, _buffer, 4)

    def _getPlayerControl_(self, addr: int) -> IPlayerControl:
        return readType(self._pm_, addr, DATA['STRUCTS']['PlayerControl'])

    def _getPlayerData_(self, addr: int) -> IPlayerData:
        return readType(self._pm_, addr, DATA['STRUCTS']['PlayerData'])

    def _getNetworkTransform_(self, addr: int) -> ICustomNetworkTransform:
        return readType(self._pm_, addr, DATA['STRUCTS']['CustomNetworkTransform'])

    def _getFullPlayer_(self,  player: IPlayerControl) -> IFullPlayerControl:
        _player = cast(IFullPlayerControl, player)
        _player['PlayerData'] = self._getPlayerData_(_player.pPlayerData)
        _player['Name'] = self._getString_(_player.PlayerData.pName)
        _player['NetworkTransform'] = self._getNetworkTransform_(
            _player.pNetworkTransform)
        _player['Tasks'] = self._getList_(
            _player.pMyTasks, DATA['STRUCTS']['Task'])
        return _player

    def _getString_(self, addr: int) -> str:
        numChars = self._pm_.read_int(
            addr + DATA['STRUCTS']['String']['length']['offset'])
        rawdata = self._pm_.read_bytes(
            addr + DATA['STRUCTS']['String']['chars']['offset'], numChars * 2)
        return rawdata.decode(encoding='utf-16').rstrip('\0')

    def _getList_(self, addr: int, _type: Dict[str, Any]) -> Sequence[Any]:
        try:
            _list = cast(IList, readType(
                self._pm_, addr, DATA['STRUCTS']['List']))
            _arrayOffset = DATA['STRUCTS']['Array']['pItems']['offset']
            _addresses = [self._pm_.read_int(_list.pArray + _arrayOffset + 4 * i)
                          for i in range(0, _list.size)]
            return [readType(self._pm_, addr, _type) for addr in _addresses]
        except Exception as e:
            pass

    def _getShipStatus_(self) -> IShipStatus:
        addr = pShipStatusStatic.resolve(self._pm_, self._gameAssemblyBase_)
        return readType(self._pm_, addr, DATA['STRUCTS']['ShipStatus'])

    def _getPlayerControlStatic_(self) -> IPlayerControlStatic:
        addr = pPlayerControlStatic.resolve(self._pm_, self._gameAssemblyBase_)
        return readType(self._pm_, addr, DATA['STRUCTS']['PlayerControlStatic'])

    def _readLocalPosAddr_(self, _addr: int) -> ILocalPos:
        return readType(self._pm_, _addr, DATA['STRUCTS']['LocalPos'])

    def _readLocalPosIdx_(self, _localPosBase: int, _idx: int) -> ILocalPos:
        return self._readLocalPosAddr_(_localPosBase + 0x100 * _idx)

    def _getGameOptions_(self) -> IGameOptions:
        addr = pGameOptions.resolve(self._pm_, self._gameAssemblyBase_)
        return readType(self._pm_, addr, DATA['STRUCTS']['GameOptions'])


GAME: Game = Game()
