from ctypes import addressof
import struct
import time
from struct import unpack
import x86
from reclassparser import _TYPES
from typing import Any, Dict, List, Sequence, TypeVar, cast, Generic
import pymem
from pymem import Pymem
from helpers import ItemHistory, Map, PointerChain
from x86 import ShellCode, ShellCodeInjector
from gametypes import *
from gamedata import DATA

pPlayerControlStatic = PointerChain([0x5c, 0])  # offset: 0x1be11cc
pShipStatusStatic = PointerChain([0x5c, 0, 0])  # offset: 0x1be114c


def calcTypeSize(_type: Dict[str, Any]) -> int:
    highestField = next(
        iter(sorted(_type.items(), key=lambda i: i[1]['offset'], reverse=True)), None)
    if not highestField:
        raise Exception('No field found!')

    data = highestField[1]
    _type = data.get('unpack')
    if _type:
        return data.get('offset') + struct.calcsize(data.get('unpack'))
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


def unpackType(pm: Pymem, rawdata: bytes, addr: 0, baseOffset: 0, _type: Dict[str, Any]):
    ret = Map()
    ret['_type'] = _type
    ret['_pm'] = pm
    ret['_addr'] = addr + baseOffset
    ret['_time'] = time.time()

    for name, meta in _type.items():  # for each field:
        if name.startswith('_'):
            continue
        ret[name] = None
        _unpack = meta.get('unpack')
        _offset = meta.get('offset')
        if _unpack:  # primitive type: unpack raw bytes
            start = baseOffset + _offset
            end = baseOffset + _offset + struct.calcsize(_unpack)
            buffer = rawdata[start: end]
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


_fn_GameObject_get_Layer: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('pGameObject')\
    .movInt32ToEaxOperand('pGameObject_get_Layer')\
    .callEax()\
    .addInt8ToEsp(0x8)\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 4)

_fn_Component_get_GameObject: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('pComponent')\
    .movInt32ToEaxOperand('pComponent_get_GameObject')\
    .callEax()\
    .addInt8ToEsp(0x8)\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 4)

_fn_PlayerControl_RpcSetHat: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt8Operand('hatId')\
    .pushInt32Operand('pPlayerControl')\
    .movInt32ToEaxOperand('pPlayerControl_RpcSetHat')\
    .callEax()\
    .addInt8ToEsp(0x0c)\
    .ret()\
    .assemble()

_fn_PlayerControl_RpcSetPet: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt8Operand('petId')\
    .pushInt32Operand('pPlayerControl')\
    .movInt32ToEaxOperand('pPlayerControl_RpcSetPet')\
    .callEax()\
    .addInt8ToEsp(0x0c)\
    .ret()\
    .assemble()

_fn_PlayerControl_RpcSetSkin: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt8Operand('skinId')\
    .pushInt32Operand('pPlayerControl')\
    .movInt32ToEaxOperand('pPlayerControl_RpcSetSkin')\
    .callEax()\
    .addInt8ToEsp(0x0c)\
    .ret()\
    .assemble()

_fn_PlayerControl_RpcCompleteTask: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt8Operand('taskId')\
    .pushInt32Operand('pPlayerControl')\
    .movInt32ToEaxOperand('pPlayerControl_RpcCompleteTask')\
    .callEax()\
    .addInt8ToEsp(0x0c)\
    .ret()\
    .assemble()

_fn_Component_get_Position: ShellCode = x86.Assembler()\
    .sehPrologue('Component_get_Transform')\
    .pushInt8(0)\
    .pushInt32Operand('pComponent')\
    .movInt32ToEaxOperand('pComponent_get_Transform')\
    .callEax()\
    .sehEpilogue('Component_get_Transform')\
    .addInt8ToEsp(0x8)\
    .testEaxEax()\
    .jumpNotZeroLabel('pComponentValid')\
    .xorEaxEax()\
    .ret()\
    .label('pComponentValid')\
    .sehPrologue('Transform_get_Position')\
    .pushInt8(0)\
    .pushEax()\
    .pushInt32Operand('pTargetBuffer')\
    .movInt32ToEaxOperand('pTransform_get_Position')\
    .callEax()\
    .sehEpilogue('Transform_get_Position')\
    .addInt8ToEsp(0xC)\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 12)

_fn_Component_set_Position: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('pComponent')\
    .movInt32ToEaxOperand('pComponent_get_Transform')\
    .callEax()\
    .addInt8ToEsp(0x8)\
    .movqQwordPtrInt32ToXmm0Operand('pNewPosition')\
    .pushInt8(0)\
    .subInt8FromEsp(0xC)\
    .movEspToEcx()\
    .pushEax()\
    .movqXmm0ToQwordPtrEcx()\
    .movEsiToDwordPtrEcx8()\
    .movInt32ToEaxOperand('pTransform_set_Position')\
    .callEax()\
    .addInt8ToEsp(0x14)\
    .ret()\
    .assemble()\
    .addBuffer('pNewPosition', 12)

_fn_Component_get_Transform: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('pComponent')\
    .movInt32ToEaxOperand('pComponent_get_Transform')\
    .callEax()\
    .addInt8ToEsp(0x8)\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 12)

_fn_GameObject_set_Layer: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('layer')\
    .pushInt32Operand('pGameObject')\
    .movInt32ToEaxOperand('pGameObject_set_Layer')\
    .callEax()\
    .addInt8ToEsp(0xC)\
    .ret()\
    .assemble()

_fn_Transform_get_Position: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('pTransform')\
    .pushInt32Operand('pTargetBuffer')\
    .movInt32ToEaxOperand('pTransform_get_Position')\
    .callEax()\
    .addInt8ToEsp(0xC)\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 12)

_fn_Transform_set_Position: ShellCode = x86.Assembler()\
    .movqQwordPtrInt32ToXmm0Operand('pNewPosition')\
    .pushInt8(0)\
    .subInt8FromEsp(0xC)\
    .movEspToEcx()\
    .pushEax()\
    .movqXmm0ToQwordPtrEcx()\
    .movEsiToDwordPtrEcx8()\
    .movInt32ToEaxOperand('pTransform_set_Position')\
    .callEax()\
    .addInt8ToEsp(0x14)\
    .ret()\
    .assemble()\
    .addBuffer('pNewPosition', 12)

_fn_PlayerTask_get_Location: ShellCode = x86.Assembler()\
    .pushInt8(0)\
    .pushInt32Operand('pTask')\
    .movInt32ToEaxOperand('pPlayerTask_get_Location')\
    .callEax()\
    .addInt8ToEsp(0xC)\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 12)

_fn_il2cpp_domain_get_: ShellCode = x86.Assembler()\
    .movInt32ToEaxOperand('pil2cpp_domain_get')\
    .callEax()\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pTargetBuffer', 4)

_fn_il2cpp_domain_assembly_open_: ShellCode = x86.Assembler()\
    .pushInt32Operand('pAssemblyName')\
    .pushInt32Operand('pDomain')\
    .movInt32ToEaxOperand('pil2cpp_domain_assembly_open')\
    .callEax()\
    .addInt8ToEsp(0x8)\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pAssemblyName', 128)\
    .addBuffer('pTargetBuffer', 4)

_fn_il2cpp_class_from_name_: ShellCode = x86.Assembler()\
    .pushInt32Operand('pClassName')\
    .pushInt32Operand('pNamespace')\
    .pushInt32Operand('pAssemblyImage')\
    .movInt32ToEaxOperand('pil2cpp_class_from_name')\
    .callEax()\
    .addInt8ToEsp(0xC)\
    .movEaxToAddrOperand('pTargetBuffer')\
    .ret()\
    .assemble()\
    .addBuffer('pClassName', 128)\
    .addBuffer('pNamespace', 128)\
    .addBuffer('pTargetBuffer', 4)


class Game:
    def __init__(self):
        self._pm_: Pymem = None
        self._PlayerControl_class_ : int = None
        self._ShipStatus_class_ : int = None
        self._gameAssemblyBase_: int = 0
        self._unityPlayerBase_: int = 0
        self._gameOptions_: IGameOptions = None
        self._shipStatus_: IShipStatus = None
        self._shipRooms_: Sequence[IPlainRoom] = []
        self._playerControlStatic_: IPlayerControlStatic = None
        self._localPlayer_: IFullPlayerControl = None
        self._allPlayers_: Sequence[IFullPlayerControl] = []
        self._injector_: ShellCodeInjector = None
        self._playerPositions_: Dict[int, ItemHistory[IVector2]] = {
            i: ItemHistory(maxAge=30, redundant=False, updateInterval=1.0) for i in range(0, 10)}
        self._playerAlive_: Dict[int, ItemHistory[bool]] = {
            i: ItemHistory(maxCount=10, redundant=False) for i in range(0, 10)}

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
    def playerPositions(self) -> Dict[int, ItemHistory[IVector2]]:
        return self._playerPositions_

    @property
    def shipRooms(self) -> Sequence[IPlainRoom]:
        return self._shipRooms_

    @ property
    def initialized(self) -> bool:
        if self._pm_ == None:
            try:
                self._pm_ = Pymem('Among Us.exe')
                self._injector_ = ShellCodeInjector(self._pm_)
                self._injector_.prepareBuffers(_fn_Component_get_GameObject)
                self._injector_.prepareBuffers(_fn_Component_get_Position)
                self._injector_.prepareBuffers(_fn_Component_get_Transform)
                self._injector_.prepareBuffers(_fn_Component_set_Position)
                self._injector_.prepareBuffers(_fn_GameObject_get_Layer)
                self._injector_.prepareBuffers(_fn_GameObject_set_Layer)
                self._injector_.prepareBuffers(
                    _fn_PlayerControl_RpcCompleteTask)
                self._injector_.prepareBuffers(_fn_PlayerControl_RpcSetHat)
                self._injector_.prepareBuffers(_fn_PlayerControl_RpcSetPet)
                self._injector_.prepareBuffers(_fn_PlayerControl_RpcSetSkin)
                self._injector_.prepareBuffers(_fn_Transform_get_Position)
                self._injector_.prepareBuffers(_fn_Transform_set_Position)
                self._injector_.prepareBuffers(_fn_il2cpp_domain_get_)
                self._injector_.prepareBuffers(_fn_il2cpp_domain_assembly_open_)
                self._injector_.prepareBuffers(_fn_il2cpp_class_from_name_)
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
        if self._PlayerControl_class_ == None:
            try:
                self._PlayerControl_class_ = self.getClassFromName(
                    'Assembly-CSharp',
                    '',
                    DATA['CLASSES']['PlayerControl']
                )
            except:
                return False
        if self._ShipStatus_class_ == None:
            try:
                self._ShipStatus_class_ = self.getClassFromName(
                    'Assembly-CSharp',
                    '',
                    DATA['CLASSES']['ShipStatus']
                )
            except:
                return False
        return True

    def update(self) -> bool:
        if not self.initialized:
            return False
        try:
            for i in range(0, 10):
                self._playerPositions_[i].update()
                self._playerAlive_[i].update()

            self._playerControlStatic_ = self._getPlayerControlStatic_()
            if not self._playerControlStatic_:
                return False

            # ShipStatus + Rooms
            self._shipStatus_ = self._getShipStatusStatic_()
            if self._shipStatus_:
                _arrType = DATA['STRUCTS']['Array']
                _lengthOffset = _arrType['max_length']['offset']
                _itemsOffset = _arrType['pItems']['offset']
                _length = self._pm_.read_int(
                    self._shipStatus_.pAllRooms + _lengthOffset)
                _roomAddresses = [self._pm_.read_int(
                    self._shipStatus_.pAllRooms + _itemsOffset + i * 4) for i in range(0, _length)]
                self._shipRooms_ = [readType(
                    self._pm_, _addr, DATA['STRUCTS']['PlainShipRoom']) for _addr in _roomAddresses]

            # Local player
            _local = self._getPlayerControl_(
                self._playerControlStatic_.pLocalPlayer)
            self._localPlayer_ = self._getFullPlayer_(_local)

            # All players
            _allPlayers = self._getList_(
                self._playerControlStatic_.pAllPlayerControls, DATA['STRUCTS']['PlayerControl'])
            self._allPlayers_ = [self._getFullPlayer_(
                player) for player in _allPlayers]
            for _player in self._allPlayers_:
                pos = _player.NetworkTransform.TargetSyncPos if _player.PlayerId != GAME.localPlayer.PlayerId else _player.NetworkTransform.PrevPosSend
                self._playerPositions_[_player.PlayerId].append(pos)
                self._playerAlive_[_player.PlayerId].append(
                    not _player.PlayerData.isDead)

            # GameOptions
            self._gameOptions_ = readType(
                self._pm_,
                self._playerControlStatic_.pGameOptions,
                DATA['STRUCTS']['GameOptions']
            )

        except Exception as e:
            self._playerControlStatic_ = None
            self._shipStatus_ = None
            self._shipRooms_ = []
            self._localPlayer_ = None
            self._allPlayers_ = []
            for _, his in self._playerPositions_.items():
                his.clear()
            for _, his in self._playerAlive_.items():
                his.clear()
            return False

        return True

    def rpcSetHat(self, hatId: int) -> None:
        global _fn_PlayerControl_RpcSetHat
        self._injector_.call(_fn_PlayerControl_RpcSetHat, {
            'hatId': hatId,
            'pPlayerControl': self._localPlayer_._addr,
            'pPlayerControl_RpcSetHat': self._gameAssemblyBase_ + DATA['OFFSETS']['PlayerControl_RpcSetHat']
        })

    def rpcSetPet(self, petId: int) -> None:
        global _fn_PlayerControl_RpcSetPet
        self._injector_.call(_fn_PlayerControl_RpcSetPet, {
            'petId': petId,
            'pPlayerControl': self._localPlayer_._addr,
            'pPlayerControl_RpcSetPet': self._gameAssemblyBase_ + DATA['OFFSETS']['PlayerControl_RpcSetPet']
        })

    def rpcSetSkin(self, skinId: int) -> None:
        global _fn_PlayerControl_RpcSetSkin
        self._injector_.call(_fn_PlayerControl_RpcSetSkin, {
            'skinId': skinId,
            'pPlayerControl': self._localPlayer_._addr,
            'pPlayerControl_RpcSetSkin': self._gameAssemblyBase_ + DATA['OFFSETS']['PlayerControl_RpcSetSkin']
        })

    def rpcCompleteTask(self, task: ITask) -> None:
        global _fn_PlayerControl_RpcCompleteTask
        self._injector_.call(_fn_PlayerControl_RpcCompleteTask, {
            'taskId': task.TaskId,
            'pPlayerControl': self._localPlayer_._addr,
            'pPlayerControl_RpcCompleteTask': self._gameAssemblyBase_ + DATA['OFFSETS']['PlayerControl_RpcCompleteTask']
        })

    def getComponentPosition(self, pComponent: int) -> StaticVector:
        global _fn_Component_get_Position
        res = self._injector_.call(_fn_Component_get_Position, {
            'pComponent': pComponent,
            'pComponent_get_Transform': self._gameAssemblyBase_ + DATA['OFFSETS']['Component_get_Transform'],
            'pTransform_get_Position': self._gameAssemblyBase_ + DATA['OFFSETS']['Transform_get_Position']
        })
        if res:
            result = readType(self._pm_, _fn_Component_get_Position.buffers['pTargetBuffer'].addr,
                              DATA['STRUCTS']['Vector2'])
            return result
        else:
            return StaticVector(0.0, 0.0)

    def setComponentPosition(self, pComponent: int, pos: StaticVector):
        global _fn_Component_set_Position
        _newPosAddr = _fn_Component_set_Position.buffers['pNewPosition'].addr
        self._pm_.write_float(_newPosAddr, pos.X)
        self._pm_.write_float(_newPosAddr + 4, pos.Y)

        self._injector_.call(_fn_Component_set_Position, {
            'pComponent': pComponent,
            'pComponent_get_Transform': self._gameAssemblyBase_ + DATA['OFFSETS']['Component_get_Transform'],
            'pTransform_set_Position': self._gameAssemblyBase_ + DATA['OFFSETS']['Transform_set_Position']
        })

    def getTransform(self, pComponent: int) -> int:
        global _fn_Component_get_Transform
        self._injector_.call(_fn_Component_get_Transform, {
            'pComponent': pComponent,
            'pComponent_get_Transform': self._gameAssemblyBase_ + DATA['OFFSETS']['Component_get_Transform']
        })
        return self._pm_.read_int(_fn_Component_get_Transform.buffers['pTargetBuffer'].addr)

    def getGameObject(self, pComponent: int) -> int:
        global _fn_Component_get_GameObject
        self._injector_.call(_fn_Component_get_GameObject, {
            'pComponent': pComponent,
            'pComponent_get_GameObject': self._gameAssemblyBase_ + DATA['OFFSETS']['Component_get_GameObject']
        })
        return self._pm_.read_int(_fn_Component_get_GameObject.buffers['pTargetBuffer'].addr)

    def getGameObjectLayer(self, pGameObject: int) -> int:
        global _fn_GameObject_get_Layer
        self._injector_.call(_fn_GameObject_get_Layer, {
            'pGameObject': pGameObject,
            'pGameObject_get_Layer': self._gameAssemblyBase_ + DATA['OFFSETS']['GameObject_get_Layer']
        })
        return self._pm_.read_int(_fn_GameObject_get_Layer.buffers['pTargetBuffer'].addr)

    def setGameObjectLayer(self, pGameObject: int, layer: int) -> None:
        global _fn_GameObject_set_Layer
        self._injector_.call(_fn_GameObject_set_Layer, {
            'layer': layer,
            'pGameObject': pGameObject,
            'pGameObject_set_Layer': self._gameAssemblyBase_ + DATA['OFFSETS']['GameObject_set_Layer']
        })

    def getTransformPosition(self, pTransform: int) -> IVector2:

        global _fn_Transform_get_Position
        self._injector_.call(_fn_Transform_get_Position, {
            'pTransform': pTransform,
            'pTransform_get_Position': self._gameAssemblyBase_ + DATA['OFFSETS']['Transform_get_Position']
        })
        result = readType(self._pm_, _fn_Component_get_Position.buffers['pTargetBuffer'].addr,
                          DATA['STRUCTS']['Vector2'])
        return result

    def setTransformPosition(self, pTransform: int, pos: IVector2):
        global _fn_Transform_set_Position
        _newPosAddr = _fn_Transform_set_Position.buffers['pNewPos'].addr
        self._pm_.write_float(_newPosAddr, pos.X)
        self._pm_.write_float(_newPosAddr + 4, pos.Y)

        self._injector_.call(_fn_Transform_set_Position, {
            'pTransform': pTransform,
            'pTransform_set_Position': self._gameAssemblyBase_ + DATA['OFFSETS']['Transform_set_Position']
        })

    def getPlayerTaskLocation(self, pTransform: int) -> IVector2:

        global _fn_PlayerTask_get_Location
        self._injector_.call(_fn_PlayerTask_get_Location, {
            'pTask': pTransform,
            'pPlayerTask_get_Location': self._gameAssemblyBase_ + DATA['OFFSETS']['PlayerTask_get_Location']
        })
        result = readType(self._pm_, _fn_Component_get_Position.buffers['pTargetBuffer'].addr,
                          DATA['STRUCTS']['Vector2'])
        return result

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
        #_player['Position'] = self.getComponentPosition(_player._addr)
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

    def _getShipStatusStatic_(self) -> IShipStatus:
        addr = pShipStatusStatic.resolve(self._pm_, self._ShipStatus_class_)
        return readType(self._pm_, addr, DATA['STRUCTS']['ShipStatus'])

    def _getPlayerControlStatic_(self) -> IPlayerControlStatic:
        addr = pPlayerControlStatic.resolve(self._pm_, self._PlayerControl_class_)
        return readType(self._pm_, addr, DATA['STRUCTS']['PlayerControlStatic'])

    def _readLocalPosAddr_(self, _addr: int) -> ILocalPos:
        return readType(self._pm_, _addr, DATA['STRUCTS']['LocalPos'])

    def _readLocalPosIdx_(self, _localPosBase: int, _idx: int) -> ILocalPos:
        return self._readLocalPosAddr_(_localPosBase + 0x100 * _idx)

    def getClassFromName(self, assemblyName: str, namespace: str, className: str) -> int:
        pDomain = self._il2cpp_domain_get_()
        pAssembly = self._il2cpp_domain_assembly_open_(pDomain, assemblyName)
        pClass = self._il2cpp_class_from_name_(pAssembly, namespace, className)
        return pClass

    def _il2cpp_domain_get_(self) -> int:
        global _fn_il2cpp_domain_get_
        self._injector_.call(_fn_il2cpp_domain_get_, {
            'pil2cpp_domain_get': self._gameAssemblyBase_ + DATA['OFFSETS']['il2cpp_domain_get']
        })
        result = self._pm_.read_int(_fn_il2cpp_domain_get_.buffers['pTargetBuffer'].addr)
        return result

    def _il2cpp_domain_assembly_open_(self, domain: int, assemblyName: str) -> int:
        global _fn_il2cpp_domain_assembly_open_
        self._injector_.writeBufferString(
            _fn_il2cpp_domain_assembly_open_.buffers['pAssemblyName'],
            assemblyName)
        self._injector_.call(_fn_il2cpp_domain_assembly_open_, {
            'pAssemblyName': _fn_il2cpp_domain_assembly_open_.buffers['pAssemblyName'].addr,
            'pDomain': domain,
            'pil2cpp_domain_assembly_open': self._gameAssemblyBase_ + DATA['OFFSETS']['il2cpp_domain_assembly_open']
        })
        result = self._pm_.read_uint(
            _fn_il2cpp_domain_assembly_open_.buffers['pTargetBuffer'].addr)
        pAssemblyImage = self._pm_.read_uint(result)
        return pAssemblyImage

    def _il2cpp_class_from_name_(self, assemblyImage: int, namespace: str, className: str) -> int:
        global _fn_il2cpp_class_from_name_
        self._injector_.writeBufferString(
            _fn_il2cpp_class_from_name_.buffers['pClassName'],
            className)
        self._injector_.writeBufferString(
            _fn_il2cpp_class_from_name_.buffers['pNamespace'],
            namespace)
        self._injector_.call(_fn_il2cpp_class_from_name_, {
            'pClassName': _fn_il2cpp_class_from_name_.buffers['pClassName'].addr,
            'pNamespace': _fn_il2cpp_class_from_name_.buffers['pNamespace'].addr,
            'pAssemblyImage': assemblyImage,
            'pil2cpp_class_from_name': self._gameAssemblyBase_ + DATA['OFFSETS']['il2cpp_class_from_name']
        })
        result = self._pm_.read_uint(
            _fn_il2cpp_class_from_name_.buffers['pTargetBuffer'].addr)
        return result

GAME: Game = Game()
