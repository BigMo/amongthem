DATA = {
    'OFFSETS': {
        'Component_get_Transform': 0x464A10,
        'Component_get_GameObject': 0x464980,
        'Transform_get_Position': 0x4477D0,
        'Transform_set_Position': 0x447C80,
        'GameObject_get_Layer': 0x466E00,
        'GameObject_set_Layer': 0x466E90,
        'PlayerControl_RpcSetHat': 0x622F60,
        'PlayerControl_RpcSetPet': 0x6231F0,
        'PlayerControl_RpcSetSkin': 0x623380,
        'PlayerControl_RpcCompleteTask': 0x622A70
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
    },
    'CONSTS': {
        'LAYER_PLAYER': 8,
        'LAYER_GHOST': 14
    }
}
