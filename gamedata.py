DATA = {
    'OFFSETS': {
        'Component_get_Transform': 0x40D4C0,
        'Component_get_GameObject': 0x40D430,
        'Transform_get_Position': 0x45A4C0,
        'Transform_set_Position': 0x45A910,
        'GameObject_get_Layer': 0x40F8C0,
        'GameObject_set_Layer': 0x40F950,
        'PlayerControl_RpcSetHat': 0x6C8FC0,
        'PlayerControl_RpcSetPet': 0x6C9250,
        'PlayerControl_RpcSetSkin': 0x6C93E0,
        'PlayerControl_RpcCompleteTask': 0x6C8AD0
    },
    'PATTERNS': {
        'PlayerControlsStatic': {
            'pattern': b'\x5F\x5B\xA1\x00\x00\x00\x00\xF6\x80', # FUCKING SUCKS
            'offset': 3
        },
        'ShipStatusStatic': {
            'pattern': b'\x74\x00\xA1\x00\x00\x00\x00\x8B\x40\x5C\x8B\x30\x85\xF6',
            'offset': 3
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
    }
}
