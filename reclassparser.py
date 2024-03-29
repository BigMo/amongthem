from typing import Sequence
import json

_TYPES = {
    'bool': {
        'format': '?',
        'type': 'bool'
    },
    'char': {
        'format': 'c',
        'type': 'bytes'
    },
    'uint8_t': {
        'format': 'B',
        'type': 'int'
    },
    'int8_t': {
        'format': 'B',
        'type': 'int'
    },
    'int32_t': {
        'format': 'i',
        'type': 'int'
    },
    'uint32_t': {
        'format': 'I',
        'type': 'int'
    },
    'float': {
        'format': 'f',
        'type': 'float'
    }
}


def parseReclass(lines: Sequence[str]):
    fields = {}
    properties = ""
    for line in lines:
        line = line.replace(';', '').replace(
            '//', '').replace('class', '').strip()
        if line.find('[') != -1:  # skip padding
            continue
        parts = line.split(' ')
        if len(parts) != 3:  # require type, name, offset
            continue
        (_type, _name, _offset) = parts
        _unpackType = _TYPES.get(_type)
        if _name.find('*') != -1:
            _unpackType = _TYPES['uint32_t']
            _name = _name.replace('*', '')

        if _unpackType:
            fields[_name] = {
                'offset': int(_offset, 0),
                'unpack': _unpackType['format']
            }
        else:
            fields[_name] = {
                'offset': int(_offset, 0),
                'type': _type
            }

        _type = _unpackType['type'] if _unpackType else _type
        properties += """@property
def %NAME%(self) -> %TYPE%:
    pass
""".replace('%NAME%', _name).replace('%TYPE%', _type)
    return (fields, properties)


lines = """	char pad_0000[12]; //0x0000
	int SystemType; //0x000C
	char pad_0010[52]; //0x0010
"""

if __name__ == '__main__':
    fields, properties = parseReclass(lines.split('\n'))
    print(json.dumps(fields, sort_keys=True, indent=4))
    print(properties)
