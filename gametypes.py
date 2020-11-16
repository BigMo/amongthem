

from typing import Sequence


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

    @property
    def Position(self) -> StaticVector:
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

    @property
    def pAllRooms(self) -> int:
        pass


class IGameOptions:
    @property
    def Speed(self) -> float:
        pass


class ILocalPos:
    @property
    def Pos(self) -> IVector2:
        pass


class IPlainRoom:
    @property
    def SystemType(self) -> int:
        pass

    @property
    def pRoomArea(self) -> int:
        pass
