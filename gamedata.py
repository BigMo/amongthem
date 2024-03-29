DATA = {
    'OFFSETS': {
        'Component_get_Transform': 0xc025a0,
        'Component_get_GameObject': 0xc02510,
        'Transform_get_Position': 0xb915c0,
        'Transform_set_Position': 0xb91a10,
        'GameObject_get_Layer': 0xc049b0,
        'GameObject_set_Layer': 0xc04a40,
        'PlayerControl_RpcSetHat': 0x8f0380,
        'PlayerControl_RpcSetPet': 0x8f0610,
        'PlayerControl_RpcSetSkin': 0x8f07a0,
        'PlayerControl_RpcCompleteTask': 0x8efe90,
        'PlayerTask_get_Location': 0x443340,
        'il2cpp_domain_get': 0x1264c0,
        'il2cpp_domain_assembly_open': 0x1264b0,
        'il2cpp_class_from_name': 0x126150,
    },
    'PATTERNS': {
        'PlayerControlsStatic': {
            'pattern': '6A 00 53 50 E8 ? ? ? ? A1 ? ? ? ? 83 C4 0C',
            #'bytes': b'\x6A.\x53\x50\xE8....\xA1....\x83\xC4\x0C',
            'bytes': b'\x85\xC9\x0F\x84....\xA1....\x6A\x00\x6A.\x8B\x40\x5C',
            'offset': 5
        },
        'ShipStatusStatic': {
            'pattern': '89 46 3C A1 ? ? ? ? 8B 40 5C 8B 00 85 C0 74',
            'bytes': b'\x89\x46\x3C\xA1....\x8B\x40\x5C\x8B\x00\x85\xC0\x74',
            'offset': 4
        }
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
            },
            'pAllRooms': {
                'offset': 140,
                'unpack': 'i'
            },
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
        },
        'PlainShipRoom': {
            "SystemType": {
                "offset": 12,
                "unpack": "i"
            },
            "pRoomArea": {
                "offset": 20,
                "unpack": "i"
            }
        }
    },
    'CONSTS': {
        'LAYER_PLAYER': 8,
        'LAYER_GHOST': 14,
        'SYSTEM_TYPES': {
            6: "Admin",
            22: "Balcony",
            29: "BoilerRoom",
            2: "Cafeteria",
            14: "Comms",
            18: "Decontamination",
            26: "Decontamination2",
            16: "Doors",
            25: "Dropship",
            7: "Electrical",
            24: "Greenhouse",
            0: "Hallway",
            21: "Laboratory",
            19: "Launchpad",
            8: "LifeSupport",
            20: "LockerRoom",
            13: "LowerEngine",
            10: "MedBay",
            5: "Nav",
            23: "Office",
            27: "Outside",
            3: "Reactor",
            17: "Sabotage",
            11: "Security",
            9: "Shields",
            15: "ShipTasks",
            28: "Specimens",
            1: "Storage",
            4: "UpperEngine",
            12: "Weapons",
        }
    },
    'CLASSES':{
        'PlayerControl': 'FFGALNAPKCD',
        'ShipStatus': 'HLBNNHFCNAJ'
    }
}
