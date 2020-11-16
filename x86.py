import ctypes
import struct
from pymem import Pymem
import pymem.ressources.kernel32
import pymem.ressources.structure
from typing import Any, Dict, Sequence, Tuple
from threading import Lock


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
        return f'@{self.offset} ("{self._format_}") = {str(self._value_)}'


class Mappable:
    def __init__(self):
        self._addr_ = None
        self._outdated_ = False

    @property
    def addr(self) -> bytes:
        return self._addr_

    @addr.setter
    def addr(self, _addr: int) -> None:
        self._addr_ = _addr

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
    def __init__(self, code: bytes, operands: Dict[str, Operand]):
        self._code_: bytes = code
        self._operands_: Dict[str, Operand] = operands
        self._addr_ = None
        self._buffers_: Dict[str, Buffer] = {}

    def updateCode(self, operandValues: Dict[str, Any] = None):
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
            _data = struct.pack('I', buffer.addr)
            _start = _op.offset
            _end = _op.offset + len(_data)
            _code[_start:_end] = _data
        if self.outdated or self._code_ != _code:
            self._code_ = bytes(_code)
            self._outdated_ = True

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
    def addr(self) -> bytes:
        return self._addr_

    @addr.setter
    def addr(self, _addr: int) -> None:
        self._addr_ = _addr

    @property
    def initialized(self) -> bool:
        return self._addr_ != None

    def __str__(self):
        _code = ' '.join([f'{b:02x}' for b in self._code_])
        _addr = f'at 0x{self._addr_:08x}' if self._addr_ else 'UNMAPPED'
        _ops = ', '.join(
            [f'"{name}"{str(o)}' for name, o in self._operands_])\
            if len(self._operands_) > 0 else 'none'
        _bufs = ', '.join(
            [f'{name} {str(buffer)}' for name, buffer in self._buffers_]
        ) if len(self._buffers_) > 0 else 'none'
        return f'Code: [{_code}] {_addr}, Operands: {_ops}, Buffers: {_bufs}'


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

    def execute(self, _addr):
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

    def call(self, code: ShellCode, operandValues: Dict[str, Any] = None):
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
                code.outdated = False
            elif code.outdated:
                self._pm_.write_bytes(code.addr, code.code, len(code.code))
                code.outdated = False
            # Execute function
            self.execute(code.addr)


class Assembler:
    def __init__(self):
        self._code_ = bytearray()
        self._operands_ = {}

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

    def assemble(self) -> ShellCode:
        shellCode = ShellCode(bytes(self._code_), self._operands_)
        self._code_ = bytearray()
        self._operands_ = {}
        return shellCode
