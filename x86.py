import ctypes
from enum import Enum
from logging import error
import struct
#import pefile
from pymem import Pymem
import pymem.ressources.kernel32
import pymem.ressources.structure
from typing import Any, Dict, List, Sequence, Tuple
from threading import Lock


class LabelRefType(Enum):
    Relative = 1,
    Absolute = 2


class LabelRef:
    def __init__(self, labelName: str, offset: int, refType: LabelRefType, format='I'):
        self._labelName_ = labelName
        self._offset_ = offset
        self._refType_ = refType
        self._format_ = format
        self._value_ = None

    @property
    def value(self) -> int:
        return self._value_

    @value.setter
    def value(self, val) -> None:
        self._value_ = val

    @property
    def format(self) -> str:
        return self._format_

    @property
    def offset(self) -> int:
        return self._offset_

    @property
    def labelName(self) -> str:
        return self._labelName_

    @property
    def refType(self) -> LabelRefType:
        return self._refType_

    def __str__(self) -> str:
        if self._value_ != None:
            return f'Ref "{self.labelName}" ({self._refType_.name}) at offset {hex(self._offset_)} set to {hex(self._value_)}'
        else:
            return f'Ref "{self.labelName}" ({self._refType_.name}) at offset {hex(self._offset_)}'


class Label:
    def __init__(self, name: str, offset: int):
        self._name_ = name
        self._offset_ = offset

    @property
    def name(self) -> str:
        return self._name_

    @property
    def offset(self) -> int:
        return self._offset_

    @offset.setter
    def offset(self, val):
        self._offset_ = val

    def __str__(self):
        return f'"{self._name_}" at offset {hex(self._offset_)}'


class Operand:
    def __init__(self, offset: int, format: str):
        self._offset_ = offset
        self._format_ = format
        self._value_ = None

    @property
    def offset(self) -> str:
        return self._offset_

    @property
    def format(self) -> str:
        return self._format_

    @property
    def value(self) -> Any:
        return self._value_

    @value.setter
    def value(self, val: Any) -> None:
        self._value_ = val

    def __str__(self) -> str:
        if self._value_ != None:
            return f'@{self.offset} ("{self._format_}") = {str(self._value_)}'
        else:
            return f'@{self.offset} ("{self._format_}") = UNSET'


class Mappable:
    def __init__(self):
        self._addr_ = None
        self._outdated_ = False

    @property
    def addr(self) -> bytes:
        return self._addr_

    @addr.setter
    def addr(self, _addr: int) -> None:
        if self._addr_ != _addr:
            self._addr_ = _addr
            self._outdated_ = True

    @property
    def mapped(self) -> bool:
        return self._addr_ != None

    @property
    def outdated(self) -> bool:
        return self._outdated_

    @outdated.setter
    def outdated(self, val: bool) -> None:
        self._outdated_ = val


class Buffer(Mappable):
    def __init__(self, size: int):
        super().__init__()
        self._size_ = size

    @property
    def size(self) -> int:
        return self._size_

    def __str__(self) -> str:
        if self.mapped:
            return f'({self._size_} bytes) at {self.addr:08x}'
        else:
            return f'({self._size_} bytes) UNMAPPED'


class ShellCode(Mappable):
    def __init__(self, code: bytes, operands: Dict[str, Operand], labels: Dict[str, Label], labelRefs: List[LabelRef]):
        super().__init__()
        self._code_: bytes = code
        self._operands_: Dict[str, Operand] = operands
        self._labels_: Dict[str, Label] = labels
        self._labelRefs_: List[LabelRef] = labelRefs
        self._buffers_: Dict[str, Buffer] = {}

    def updateCode(self, operandValues: Dict[str, Any] = None, forceCodeGen: bool = False):
        _code = bytearray(self._code_)
        if operandValues:
            for name, value in operandValues.items():
                _op = self._operands_.get(name)
                if not _op:
                    raise Exception(f'Unknown operand "{name}"!')
                if _op.value == value:  # Don't write unchanged values
                    continue
                _op.value = value
                _data = struct.pack(_op.format, value)
                _start = _op.offset
                _end = _op.offset + len(_data)
                _code[_start:_end] = _data
                self.outdated = True
        for name, buffer in self._buffers_.items():
            _op = self._operands_.get(name)
            if not _op:
                raise Exception(f'Buffer "{name}" not mapped to any operands!')
            if buffer.addr == _op.value:
                continue
            _op.value = buffer.addr
            _data = struct.pack('I', buffer.addr)
            _start = _op.offset
            _end = _op.offset + len(_data)
            _code[_start:_end] = _data
            self.outdated = True
        if self.resolveLabels() or forceCodeGen:
            for labelRef in self._labelRefs_:
                _data = struct.pack(labelRef.format, labelRef.value)
                _start = labelRef.offset
                _end = labelRef.offset + len(_data)
                _code[_start:_end] = _data
        if self.outdated or self._code_ != _code or forceCodeGen:
            self._code_ = bytes(_code)
            self._outdated_ = True

    def resolveLabels(self) -> bool:
        if not self.mapped:
            return False

        hasChanged = False
        for labelRef in self._labelRefs_:
            _label = self._labels_.get(labelRef.labelName)
            if not _label:
                raise Exception(f'Missing label "{labelRef.labelName}"!')

            if labelRef.refType == LabelRefType.Absolute:
                value = self.addr + _label.offset
            else:
                size = struct.calcsize(labelRef.format)
                start = labelRef.offset + size
                end = _label.offset
                value = end - start

            if value != labelRef.value:
                hasChanged = True
                labelRef.value = value
        if hasChanged:
            self.outdated = True
        return hasChanged

    def addBuffer(self, name: str, size: int) -> 'ShellCode':
        self._buffers_[name] = Buffer(size)
        return self

    @property
    def code(self) -> bytes:
        return self._code_

    @property
    def operands(self) -> Dict[str, Operand]:
        return self._operands_

    @property
    def buffers(self) -> Dict[str, Buffer]:
        return self._buffers_

    @property
    def labels(self) -> Dict[str, Label]:
        return self._labels_

    @property
    def labelReferences(self) -> List[LabelRef]:
        return self._labelRefs_

    def __str__(self):
        _code = ' '.join([f'{b:02x}' for b in self._code_])
        _addr = f'at 0x{self.addr:08x}' if self.addr else 'UNMAPPED'
        _ops = ', '.join(
            [f'"{name}"{str(o)}' for name, o in self._operands_.items()])\
            if len(self._operands_) > 0 else 'none'
        _labels = ', '.join(
            [str(l) for _, l in self._labels_.items()]
        ) if len(self._labels_) > 0 else 'none'
        _labelRefs = ', '.join([str(lRef) for lRef in self._labelRefs_]) if len(
            self._labelRefs_) > 0 else 'none'
        _bufs = ', '.join(
            [f'{name} {str(buffer)}' for name,
             buffer in self._buffers_.items()]
        ) if len(self._buffers_) > 0 else 'none'
        return f'Code: [{_code}] {_addr}; Operands: {_ops}; Buffers: {_bufs}; Labels: {_labels}; LabelReferences: {_labelRefs}'


class ShellCodeInjector:
    def __init__(self, pm: Pymem):
        self._pm_ = pm
        self._lock_: Lock = Lock()

    @property
    def handle(self):
        return self._pm_.process_handle

    def alloc(self, _numBytes: int) -> int:
        return pymem.ressources.kernel32.VirtualAllocEx(
            self.handle,
            0,
            _numBytes,
            pymem.ressources.structure.MEMORY_STATE.MEM_COMMIT.value | pymem.ressources.structure.MEMORY_STATE.MEM_RESERVE.value,
            pymem.ressources.structure.MEMORY_PROTECTION.PAGE_EXECUTE_READWRITE.value
        )

    def free(self, _addr: int, _numBytes: int):
        pymem.ressources.kernel32.VirtualFreeEx(
            self.handle,
            _addr,
            _numBytes,
            pymem.ressources.structure.MEMORY_STATE.MEM_RELEASE.value
        )

    def execute(self, _addr) -> int:
        thread_h = pymem.ressources.kernel32.CreateRemoteThread(
            self.handle, None, 0, _addr, 0, 0, None
        )
        pymem.ressources.kernel32.WaitForSingleObject(thread_h, -1)
        exitcode = ctypes.c_ulong(0)
        pymem.ressources.kernel32.GetExitCodeThread(
            thread_h,
            ctypes.byref(exitcode)
        )
        return exitcode.value

    def prepareBuffers(self, code: ShellCode):
        for _, buffer in code.buffers.items():
            if not buffer.mapped:
                buffer.addr = self.alloc(buffer._size_)

    def call(self, code: ShellCode, operandValues: Dict[str, Any] = None) -> int:
        with self._lock_:  # We don't want multiple threads to fck up the shellcode...
            # Alloc buffers and write them to the func code if necessary
            _buffers = [b for _, b in code.buffers.items() if not b.mapped]
            if len(_buffers) > 0:
                for buffer in _buffers:
                    buffer.addr = self.alloc(buffer._size_)
            code.updateCode(operandValues)
            # Write func to mem if neccessary
            if not code.mapped:
                code.addr = self.alloc(len(code.code))
                self._pm_.write_bytes(code.addr, code.code, len(code.code))
                code.outdated = code.resolveLabels()
                code.updateCode(forceCodeGen=True)
            if code.outdated:
                self._pm_.write_bytes(code.addr, code.code, len(code.code))
                code.outdated = False
            # Execute function
            return self.execute(code.addr)

    def writeBufferString(self, buffer: Buffer, text: str):
        data = (text + '\0').encode(encoding='ascii')
        if buffer.size < len(data):
            raise Exception('Buffer too small')
        self._pm_.write_bytes(buffer.addr, data, len(data))


class Assembler:
    def __init__(self):
        self._code_ = bytearray()
        self._operands_: Dict[str, Operand] = {}
        self._labels_: Dict[str, Label] = {}
        self._labelRefs_: List[LabelRef] = []

    def pushInt8(self, _val) -> 'Assembler':
        self._code_ += b'\x6A' + struct.pack('B', _val)  # push _val
        return self

    def pushInt8Operand(self, _name) -> 'Assembler':
        self._operands_[_name] = Operand(len(self._code_) + 1, 'B')
        self._code_ += b'\x6A\x00'  # push _val
        return self

    def pushInt32(self, _val) -> 'Assembler':
        self._code_ += b'\x68' + struct.pack('I', _val)  # push _val
        return self

    def pushInt32Operand(self, _name) -> 'Assembler':
        self._operands_[_name] = Operand(len(self._code_) + 1, 'I')
        self._code_ += b'\x68\x00\x00\x00\x00'  # push _val
        return self

    def pushEax(self) -> 'Assembler':
        self._code_ += b'\x50'  # push eax
        return self

    def movInt32ToEax(self, _val) -> 'Assembler':
        self._code_ += b'\xB8' + struct.pack('I', _val)  # mov eax, _val
        return self

    def movInt32ToEaxOperand(self, _name) -> 'Assembler':
        self._operands_[_name] = Operand(len(self._code_) + 1, 'I')
        self._code_ += b'\xB8\x00\x00\x00\x00'  # mov eax, _val
        return self

    def movEaxToAddr(self, _addr) -> 'Assembler':
        self._code_ += b'\xA3' + struct.pack('I', _addr)  # mov [_addr], eax
        return self

    def movEaxToAddrOperand(self, _name) -> 'Assembler':
        self._operands_[_name] = Operand(len(self._code_) + 1, 'I')
        self._code_ += b'\xA3\x00\x00\x00\x00'  # mov [_addr], eax
        return self

    def movEspToEcx(self) -> 'Assembler':
        self._code_ += b'\x89\xE1'  # mov ecx, esp
        return self

    def movqXmm0ToQwordPtrEcx(self) -> 'Assembler':
        self._code_ += b'\x66\x0F\xD6\x01'  # movq qword ptr [ecx], xmm0
        return self

    def movqQwordPtrInt32ToXmm0(self, _addr) -> 'Assembler':
        self._code_ += b'\xF3\x0F\x7E\x05' + \
            struct.pack('I', _addr)  # movq xmm0, qword ptr [_addr]
        return self

    def movqQwordPtrInt32ToXmm0Operand(self, _name) -> 'Assembler':
        self._operands_[_name] = Operand(len(self._code_) + 4, 'I')
        # movq xmm0, qword ptr [_addr]
        self._code_ += b'\xF3\x0F\x7E\x05\x00\x00\x00\x00'
        return self

    def movEsiToDwordPtrEcx8(self) -> 'Assembler':
        self._code_ += b'\x89\x71\x08'  # mov dword ptr [ecx + 8], esi
        return self

    def callEax(self) -> 'Assembler':
        self._code_ += b'\xFF\xD0'  # call eax
        return self

    def testEaxEax(self) -> 'Assembler':
        self._code_ += b'\x85\xC0'  # test eax, eax -> is eax non-zero?
        return self

    def incEax(self) -> 'Assembler':
        self._code_ += b'\x40'  # inc eax
        return self

    def xorEaxEax(self) -> 'Assembler':
        self._code_ += b'\x31\xC0'  # xor eax, eax
        return self

    def callInt32Operand(self, _name) -> 'Assembler':
        self._operands_[_name] = Operand(len(self._code_) + 2, 'I')
        self._code_ += b'\xFF\x15\x00\x00\x00\x00'  # add esp, _val
        return self

    def addInt8ToEsp(self, _val) -> 'Assembler':
        self._code_ += b'\x83\xC4' + struct.pack('B', _val)  # add esp, _val
        return self

    def addInt8ToEspOperand(self, _name) -> 'Assembler':
        self._operands_[_name] = Operand(len(self._code_) + 2, 'B')
        self._code_ += b'\x83\xC4\x00'  # add esp, _val
        return self

    def subInt8FromEsp(self, _val) -> 'Assembler':
        self._code_ += b'\x83\xEC' + struct.pack('B', _val)  # sub esp, _val
        return self

    def subInt8FromEspOperand(self, _name) -> 'Assembler':
        self._operands_[_name] = Operand(len(self._code_) + 2, 'B')
        self._code_ += b'\x83\xEC\x00'  # sub esp, _val
        return self

    def ret(self) -> 'Assembler':
        self._code_ += b'\xC3'  # ret
        return self

    def pushLabel(self, name) -> 'Assembler':
        self._code_ += b'\x68'  # push...
        return self._labelRef_(name, LabelRefType.Absolute)  # ...[name]

    def sehPrologue(self, name=None) -> 'Assembler':
        _lblHandler = f'_SEHANDLER_{name}_' if name else '_SEHANDLER_'
        # PUSH [ERRORHANDLER] - pointer to error handler
        self.pushLabel(_lblHandler)
        # PUSH DWORD PTR FS:[0]   - save old SE handler
        self._code_ += b'\x64\xFF\x35\x00\x00\x00\x00'
        # MOV DWORD PTR FS:[0],ESP - set new seh record
        self._code_ += b'\x64\x89\x25\x00\x00\x00\x00'
        return self

    def sehEpilogue(self, name=None) -> 'Assembler':
        _lblHandler = f'_SEHANDLER_{name}_' if name else '_SEHANDLER_'
        _lblNoError = f'_SEH_NO_ERROR_{name}_' if name else '_SEH_NO_ERROR_'

        self.jumpShortLabel(_lblNoError)
        self.label(_lblHandler)
        # MOV ESP,DWORD PTR SS:[ESP+8] - error handler here... restore esp
        self._code_ += b'\x8B\x64\xE4\x08'
        # XOR EAX,EAX  - set eax
        self.xorEaxEax()
        # SUB EAX,1      to -1
        self._code_ += b'\x83\xE8\x01'
        self.label(_lblNoError)
        # POP DWORD PTR FS:[0] - jump here if no error
        self._code_ += b'\x64\x8F\x05\x00\x00\x00\x00'
        # ADD ESP,4
        self._code_ += b'\x83\xC4\x04'
        return self

    def jumpShortInt8(self, _val) -> 'Assembler':
        self._code_ += b'\xEB' + struct.pack('B', _val)
        return self

    def jumpShortLabel(self, label) -> 'Assembler':
        self._code_ += b'\xEB'
        return self._labelRef_(label, LabelRefType.Relative, 'B')

    def jumpNotZeroLabel(self, label) -> 'Assembler':
        self._code_ += b'\x75'  # jz [label]
        return self._labelRef_(label, LabelRefType.Relative, 'B')

    def jumpLessLabel(self, label) -> 'Assembler':
        self._code_ += b'\x7C'  # jl [label] -> is SF != OF
        return self._labelRef_(label, LabelRefType.Relative, 'B')

    def jumpNotLessLabel(self, label) -> 'Assembler':
        self._code_ += b'\x7D'  # jnl [label] -> is SF == OF
        return self._labelRef_(label, LabelRefType.Relative, 'B')

    def _labelRef_(self, name: str, refType: LabelRefType, format='I') -> 'Assembler':
        self._labelRefs_.append(
            LabelRef(name, len(self._code_), refType, format))
        size = struct.calcsize(format)
        self._code_ += b'\x00' * size
        return self

    def label(self, name: str) -> 'Assembler':
        self._labels_[name] = Label(name, len(self._code_))
        return self

    def assemble(self) -> ShellCode:
        shellCode = ShellCode(bytes(self._code_),
                              self._operands_, self._labels_, self._labelRefs_)
        self._code_ = bytearray()
        self._operands_ = {}
        return shellCode


# class RemoteTools:
#     @staticmethod
#     def getRemoteModule(pm: Pymem, moduleName: str) -> Tuple[int, int]:
#         for module in pm.list_modules():
#             if module.name.lower() == moduleName.lower():
#                 return (module.lpBaseOfDll, module.SizeOfImage)
#         return None

#     _fn_get_proc_address_ = Assembler()\
#         .pushInt32Operand('pProcName')\
#         .pushInt32Operand('pModuleAddress')\
#         .movInt32ToEaxOperand('pGetProcAddress')\
#         .callEax()\
#         .movEaxToAddrOperand('pTargetBuffer')\
#         .ret()\
#         .assemble()\
#         .addBuffer('pTargetBuffer', 4)\
#         .addBuffer('pProcName', 128)

#     @staticmethod
#     def getRemoteProcAddress(injector: ShellCodeInjector, pModule: int, procName: str) -> int:
#         injector.prepareBuffers(RemoteTools._fn_get_proc_address_)
#         remoteK32, size = RemoteTools.getRemoteModule(
#             injector._pm_, 'kernel32.dll')
#         blob = injector._pm_.read_bytes(remoteK32, size)

#         pe = pefile.PE(data=blob)
#         offset = next(filter(lambda exp: exp.name == 'GetProcAddress',
#                              pe.DIRECTORY_ENTRY_EXPORT.symbols), None)

#         pGetProcAddress = remoteK32 + offset  # 0x1f550 #offset
#         injector.writeBufferString(
#             RemoteTools._fn_get_proc_address_.buffers['pProcName'],
#             procName
#         )
#         injector.call(RemoteTools._fn_get_proc_address_,
#                       {
#                           'pProcName': RemoteTools._fn_get_proc_address_.buffers['pProcName'].addr,
#                           'pModuleAddress': pModule,
#                           'pGetProcAddress': pGetProcAddress
#                       })
#         return injector._pm_.read_uint(RemoteTools._fn_get_proc_address_.buffers['pTargetBuffer'].addr)
