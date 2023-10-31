# -*- encoding: utf-8 -*-

from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
from app import db, login_manager
from app.base import blueprint
import decimal
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User
from app.base.util import bip_39_full_list, verify_pass
import requests
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Changes, Bip44Coins
import hashlib
from secrets import randbits
from typing import Union, List, Tuple
import binascii
import random
from cryptography.fernet import Fernet
import json
from random import getrandbits
import xrpl.account
from mnemonic import Mnemonic
from xrpl.account import get_next_valid_seq_number
from xrpl.asyncio.clients import XRPLRequestFailureException
from xrpl.clients import JsonRpcClient
from xrpl.core import keypairs
from xrpl.core.binarycodec import encode_for_signing
from xrpl.core.keypairs import sign, derive_classic_address
from xrpl.ledger import get_fee, get_latest_validated_ledger_sequence
from xrpl.models import Payment, AccountDelete
from xrpl.wallet import Wallet
import base58
from mnemonic import Mnemonic
from mnemonic import Mnemonic
from secrets import randbits
from binascii import hexlify
from hashlib import sha256
from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir
from xrpl.core.keypairs import derive_classic_address
from xrpl.wallet import generate_faucet_wallet, Wallet
#pycryptodome
from binascii import hexlify, unhexlify
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from getpass import getpass
from Crypto.Hash import SHA256
import binascii
import random
from operator import mul
from functools import reduce
from Cryptodome.Util.number import getPrime
from Cryptodome.Util.number import getPrime, inverse
import sys
from bip32 import BIP32
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountTx
from xrpl.transaction import (
    autofill_and_sign,
    submit_and_wait
)

@blueprint.route('/')
def route_default():
    return render_template('setup.html')


@blueprint.route('/generate-fernet-encryption-key')
def fernet_encryption():
    key = Fernet.generate_key()
    return {'encryption_key': key.decode()}


#For secure usage, generate a one_time encryption key and store it in environment 
#one_time_encryption_key = fernet_encryption()['encryption_key']

one_time_encryption_key = "sWhxokO2oziiwASG2Z3pcgFQWHHv7q4P6aY7yfVaurA="
cipher_suite = Fernet(one_time_encryption_key)
RPC = "https://xrplcluster.com/"
CLIENT = JsonRpcClient(RPC)


#Implement this function anywhere to send webhooks to a server. 
def send_webhook(url, payload):
    headers = {'content-type': 'application/json'}
    payload_compressed = json.dumps(payload)
    r = requests.post(url, data=payload_compressed, headers = headers)
    return


@blueprint.route('/ecsda/generate-shard')
def generate_ecsda_shard():
    url = "https://poof-mpc-0612eded1bd9.herokuapp.com/gen-key-configs" #temporary test MPC endpoint
    payload = json.dumps({
        "ids": ["a", "b", "c"],
        "threshold": 2
    })
    headers = {
        'Authorization': '', 
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return jsonify(response.json())

@blueprint.route('/ecsda/generate-pre-signature')
def generate_pre_signature(escda_shards = None):
    url = "https://poof-mpc-0612eded1bd9.herokuapp.com/gen-pre-sigs" #temporary test MPC endpoint

    #Example of generating pre signature used for final MPC round based on XRPL message hash
    payload = json.dumps({
        "ids": ["a", "b", "c"],
        "rawKeyConfigs": [
        "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"
    ]
    })
    headers = {
        'Authorization': '', 
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return jsonify(response.json()) 
    #RawPreSignatures is Output


@blueprint.route('/ecsda/generate-ecsda-signature')
def combine_pre_signature(message_to_sign = None):
    url = "https://poof-mpc-0612eded1bd9.herokuapp.com/presign" #Working on configuring payment dict to XRPL format

    #Example of generating pre signature used for final MPC round based on XRPL message hash
    payload = {
        "ids": ["a", "b", "c"],
        "rawKeyConfigs": [
        "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"    ],
    "preSignatures": [
        {
            "ID": "BmFIloUnbQKPzxY+BeA9/Jza76b+NqHj7VIaibjvNlg=",
            "R": {
                "Value": {
                    "X": {
                        "N": [
                            19001028,
                            44057912,
                            25148207,
                            21595333,
                            6953532,
                            58139213,
                            28195211,
                            4267053,
                            21269951,
                            174852
                        ]
                    },
                    "Y": {
                        "N": [
                            2715828,
                            19673003,
                            48892179,
                            180009,
                            21891523,
                            53996068,
                            66823562,
                            15306934,
                            3860138,
                            3785864
                        ]
                    },
                    "Z": {
                        "N": [
                            26555101,
                            57770305,
                            23307494,
                            21914232,
                            18235477,
                            51635437,
                            60612131,
                            13681302,
                            2117328,
                            3196282
                        ]
                    }
                }
            },
            "RBar": {
                "Points": {
                    "a": {
                        "Value": {
                            "X": {
                                "N": [
                                    47363964,
                                    8252088,
                                    10527892,
                                    29805999,
                                    56339520,
                                    4877060,
                                    4990442,
                                    60038706,
                                    4995027,
                                    1260089
                                ]
                            },
                            "Y": {
                                "N": [
                                    33425460,
                                    37268593,
                                    18015315,
                                    39388645,
                                    12577694,
                                    13638743,
                                    8292847,
                                    9977253,
                                    13656404,
                                    3617740
                                ]
                            },
                            "Z": {
                                "N": [
                                    34176086,
                                    12151725,
                                    22903736,
                                    46332815,
                                    49400338,
                                    43267327,
                                    42829166,
                                    9228503,
                                    40403901,
                                    2965227
                                ]
                            }
                        }
                    },
                    "b": {
                        "Value": {
                            "X": {
                                "N": [
                                    24965699,
                                    15776950,
                                    26732707,
                                    1376776,
                                    64201060,
                                    10693161,
                                    31123295,
                                    21276650,
                                    45298339,
                                    3069587
                                ]
                            },
                            "Y": {
                                "N": [
                                    18438530,
                                    25186741,
                                    6494980,
                                    56556178,
                                    22573434,
                                    17987174,
                                    18384647,
                                    12952554,
                                    56152115,
                                    3912208
                                ]
                            },
                            "Z": {
                                "N": [
                                    27518129,
                                    63668206,
                                    34361098,
                                    3770675,
                                    8785819,
                                    58818992,
                                    54472905,
                                    31668346,
                                    52512655,
                                    2643534
                                ]
                            }
                        }
                    },
                    "c": {
                        "Value": {
                            "X": {
                                "N": [
                                    56485157,
                                    18832101,
                                    960527,
                                    15373943,
                                    50117309,
                                    64553138,
                                    18858108,
                                    166782,
                                    63750057,
                                    1800355
                                ]
                            },
                            "Y": {
                                "N": [
                                    10237619,
                                    1160753,
                                    46358699,
                                    46728336,
                                    48957690,
                                    15963407,
                                    8544278,
                                    24592285,
                                    26093648,
                                    919584
                                ]
                            },
                            "Z": {
                                "N": [
                                    53135159,
                                    3300809,
                                    5834081,
                                    57302798,
                                    47089071,
                                    15676848,
                                    20524202,
                                    4333687,
                                    35360968,
                                    53187
                                ]
                            }
                        }
                    }
                }
            },
            "S": {
                "Points": {
                    "a": {
                        "Value": {
                            "X": {
                                "N": [
                                    28588891,
                                    62819955,
                                    62606161,
                                    54003227,
                                    10402947,
                                    22325780,
                                    13438483,
                                    11342197,
                                    34316324,
                                    1754719
                                ]
                            },
                            "Y": {
                                "N": [
                                    106468701,
                                    82839468,
                                    95301755,
                                    74993192,
                                    131718512,
                                    79087364,
                                    133815895,
                                    121555618,
                                    87730643,
                                    8140284
                                ]
                            },
                            "Z": {
                                "N": [
                                    1,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0
                                ]
                            }
                        }
                    },
                    "b": {
                        "Value": {
                            "X": {
                                "N": [
                                    64748852,
                                    13421237,
                                    59520067,
                                    24596744,
                                    55124023,
                                    63913471,
                                    33386105,
                                    60969943,
                                    3907058,
                                    3077126
                                ]
                            },
                            "Y": {
                                "N": [
                                    83937442,
                                    113037451,
                                    129089692,
                                    70986839,
                                    97257675,
                                    92789963,
                                    83000449,
                                    117543366,
                                    72098123,
                                    7786998
                                ]
                            },
                            "Z": {
                                "N": [
                                    1,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0
                                ]
                            }
                        }
                    },
                    "c": {
                        "Value": {
                            "X": {
                                "N": [
                                    36776061,
                                    14298779,
                                    2122907,
                                    12523458,
                                    5038638,
                                    59445288,
                                    382845,
                                    14735803,
                                    21061785,
                                    3914866
                                ]
                            },
                            "Y": {
                                "N": [
                                    4043038,
                                    10672298,
                                    46279798,
                                    36005435,
                                    34268702,
                                    49810597,
                                    14480014,
                                    42873547,
                                    23262413,
                                    3354189
                                ]
                            },
                            "Z": {
                                "N": [
                                    38602208,
                                    23124198,
                                    23782686,
                                    48432615,
                                    1744487,
                                    10710507,
                                    45644792,
                                    7636620,
                                    16569367,
                                    171448
                                ]
                            }
                        }
                    }
                }
            },
            "KShare": {},
            "ChiShare": {}
        },
        {
            "ID": "BmFIloUnbQKPzxY+BeA9/Jza76b+NqHj7VIaibjvNlg=",
            "R": {
                "Value": {
                    "X": {
                        "N": [
                            14611617,
                            2792256,
                            51428145,
                            21855406,
                            61379451,
                            9364755,
                            4605175,
                            55773066,
                            9246842,
                            2547409
                        ]
                    },
                    "Y": {
                        "N": [
                            2510078,
                            44404147,
                            59367605,
                            25382983,
                            24572923,
                            40032953,
                            5217765,
                            2823582,
                            21425858,
                            236718
                        ]
                    },
                    "Z": {
                        "N": [
                            48648614,
                            29244449,
                            24941017,
                            61467938,
                            47485992,
                            36457069,
                            45610511,
                            57274481,
                            42464483,
                            2221673
                        ]
                    }
                }
            },
            "RBar": {
                "Points": {
                    "a": {
                        "Value": {
                            "X": {
                                "N": [
                                    47363964,
                                    8252088,
                                    10527892,
                                    29805999,
                                    56339520,
                                    4877060,
                                    4990442,
                                    60038706,
                                    4995027,
                                    1260089
                                ]
                            },
                            "Y": {
                                "N": [
                                    33425460,
                                    37268593,
                                    18015315,
                                    39388645,
                                    12577694,
                                    13638743,
                                    8292847,
                                    9977253,
                                    13656404,
                                    3617740
                                ]
                            },
                            "Z": {
                                "N": [
                                    34176086,
                                    12151725,
                                    22903736,
                                    46332815,
                                    49400338,
                                    43267327,
                                    42829166,
                                    9228503,
                                    40403901,
                                    2965227
                                ]
                            }
                        }
                    },
                    "b": {
                        "Value": {
                            "X": {
                                "N": [
                                    2711254,
                                    32034154,
                                    6752887,
                                    54844293,
                                    48924582,
                                    3572735,
                                    62591022,
                                    26415100,
                                    33492512,
                                    774436
                                ]
                            },
                            "Y": {
                                "N": [
                                    42067489,
                                    12733660,
                                    8243733,
                                    61135404,
                                    34988531,
                                    46816206,
                                    28812563,
                                    18169020,
                                    40436285,
                                    3958138
                                ]
                            },
                            "Z": {
                                "N": [
                                    20874348,
                                    57843372,
                                    63181606,
                                    18213272,
                                    30439283,
                                    37161298,
                                    479752,
                                    30019564,
                                    45320397,
                                    2609070
                                ]
                            }
                        }
                    },
                    "c": {
                        "Value": {
                            "X": {
                                "N": [
                                    368605,
                                    53297351,
                                    3176283,
                                    54148208,
                                    65389194,
                                    13794657,
                                    15039069,
                                    41254773,
                                    58685620,
                                    2215357
                                ]
                            },
                            "Y": {
                                "N": [
                                    36178465,
                                    39426200,
                                    8450832,
                                    61086435,
                                    63735972,
                                    192542,
                                    20055069,
                                    15822449,
                                    35700200,
                                    573708
                                ]
                            },
                            "Z": {
                                "N": [
                                    42898550,
                                    28494389,
                                    24480286,
                                    15397583,
                                    26569155,
                                    22299958,
                                    33370058,
                                    54359744,
                                    46628148,
                                    3862872
                                ]
                            }
                        }
                    }
                }
            },
            "S": {
                "Points": {
                    "a": {
                        "Value": {
                            "X": {
                                "N": [
                                    28588891,
                                    62819955,
                                    62606161,
                                    54003227,
                                    10402947,
                                    22325780,
                                    13438483,
                                    11342197,
                                    34316324,
                                    1754719
                                ]
                            },
                            "Y": {
                                "N": [
                                    106468701,
                                    82839468,
                                    95301755,
                                    74993192,
                                    131718512,
                                    79087364,
                                    133815895,
                                    121555618,
                                    87730643,
                                    8140284
                                ]
                            },
                            "Z": {
                                "N": [
                                    1,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0
                                ]
                            }
                        }
                    },
                    "b": {
                        "Value": {
                            "X": {
                                "N": [
                                    47307542,
                                    8219550,
                                    21815817,
                                    25242775,
                                    65082208,
                                    1580820,
                                    49375227,
                                    26008973,
                                    52363441,
                                    397654
                                ]
                            },
                            "Y": {
                                "N": [
                                    65923897,
                                    24974612,
                                    66185115,
                                    8162613,
                                    151971,
                                    14252474,
                                    29911867,
                                    31690903,
                                    49140865,
                                    3776221
                                ]
                            },
                            "Z": {
                                "N": [
                                    35199334,
                                    53418137,
                                    35612365,
                                    13337423,
                                    66222104,
                                    19436575,
                                    65234437,
                                    11818200,
                                    54763026,
                                    1979960
                                ]
                            }
                        }
                    },
                    "c": {
                        "Value": {
                            "X": {
                                "N": [
                                    20125623,
                                    20176707,
                                    37115545,
                                    29480970,
                                    20550743,
                                    52522447,
                                    8329405,
                                    21136545,
                                    65772732,
                                    2682882
                                ]
                            },
                            "Y": {
                                "N": [
                                    130247841,
                                    76848440,
                                    87866398,
                                    79822509,
                                    134045275,
                                    132632185,
                                    110300858,
                                    114693823,
                                    101800056,
                                    5145087
                                ]
                            },
                            "Z": {
                                "N": [
                                    1,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0
                                ]
                            }
                        }
                    }
                }
            },
            "KShare": {},
            "ChiShare": {}
        },
        {
            "ID": "BmFIloUnbQKPzxY+BeA9/Jza76b+NqHj7VIaibjvNlg=",
            "R": {
                "Value": {
                    "X": {
                        "N": [
                            38883915,
                            55768598,
                            6455125,
                            33495137,
                            47329899,
                            38755125,
                            48537807,
                            67054116,
                            2432461,
                            3295976
                        ]
                    },
                    "Y": {
                        "N": [
                            66939364,
                            63480452,
                            44711996,
                            21806924,
                            18036846,
                            26881085,
                            26779375,
                            17236071,
                            13249372,
                            2037936
                        ]
                    },
                    "Z": {
                        "N": [
                            2704374,
                            30420889,
                            24055597,
                            2835015,
                            2670330,
                            31957014,
                            20658653,
                            20185779,
                            54207990,
                            3875637
                        ]
                    }
                }
            },
            "RBar": {
                "Points": {
                    "a": {
                        "Value": {
                            "X": {
                                "N": [
                                    2212023,
                                    33755673,
                                    28289216,
                                    46175856,
                                    51510304,
                                    22066261,
                                    21066354,
                                    16525170,
                                    66694122,
                                    670906
                                ]
                            },
                            "Y": {
                                "N": [
                                    7307590,
                                    29018357,
                                    39456803,
                                    31549512,
                                    14890083,
                                    6383727,
                                    66304847,
                                    56805719,
                                    10451629,
                                    641744
                                ]
                            },
                            "Z": {
                                "N": [
                                    8282888,
                                    64697794,
                                    47976551,
                                    57768108,
                                    25923104,
                                    66102309,
                                    34887417,
                                    54953778,
                                    39650629,
                                    3701964
                                ]
                            }
                        }
                    },
                    "b": {
                        "Value": {
                            "X": {
                                "N": [
                                    24965699,
                                    15776950,
                                    26732707,
                                    1376776,
                                    64201060,
                                    10693161,
                                    31123295,
                                    21276650,
                                    45298339,
                                    3069587
                                ]
                            },
                            "Y": {
                                "N": [
                                    18438530,
                                    25186741,
                                    6494980,
                                    56556178,
                                    22573434,
                                    17987174,
                                    18384647,
                                    12952554,
                                    56152115,
                                    3912208
                                ]
                            },
                            "Z": {
                                "N": [
                                    27518129,
                                    63668206,
                                    34361098,
                                    3770675,
                                    8785819,
                                    58818992,
                                    54472905,
                                    31668346,
                                    52512655,
                                    2643534
                                ]
                            }
                        }
                    },
                    "c": {
                        "Value": {
                            "X": {
                                "N": [
                                    368605,
                                    53297351,
                                    3176283,
                                    54148208,
                                    65389194,
                                    13794657,
                                    15039069,
                                    41254773,
                                    58685620,
                                    2215357
                                ]
                            },
                            "Y": {
                                "N": [
                                    36178465,
                                    39426200,
                                    8450832,
                                    61086435,
                                    63735972,
                                    192542,
                                    20055069,
                                    15822449,
                                    35700200,
                                    573708
                                ]
                            },
                            "Z": {
                                "N": [
                                    42898550,
                                    28494389,
                                    24480286,
                                    15397583,
                                    26569155,
                                    22299958,
                                    33370058,
                                    54359744,
                                    46628148,
                                    3862872
                                ]
                            }
                        }
                    }
                }
            },
            "S": {
                "Points": {
                    "a": {
                        "Value": {
                            "X": {
                                "N": [
                                    27858176,
                                    33023206,
                                    10491504,
                                    34983154,
                                    23815889,
                                    5951778,
                                    502644,
                                    2468216,
                                    50015506,
                                    343464
                                ]
                            },
                            "Y": {
                                "N": [
                                    16587017,
                                    15336033,
                                    12638139,
                                    24294594,
                                    19179033,
                                    25968759,
                                    61558879,
                                    29089239,
                                    46541854,
                                    3294985
                                ]
                            },
                            "Z": {
                                "N": [
                                    37596635,
                                    1142588,
                                    28815169,
                                    8079073,
                                    19445302,
                                    26496280,
                                    17863445,
                                    30253862,
                                    26769613,
                                    2392229
                                ]
                            }
                        }
                    },
                    "b": {
                        "Value": {
                            "X": {
                                "N": [
                                    64748852,
                                    13421237,
                                    59520067,
                                    24596744,
                                    55124023,
                                    63913471,
                                    33386105,
                                    60969943,
                                    3907058,
                                    3077126
                                ]
                            },
                            "Y": {
                                "N": [
                                    83937442,
                                    113037451,
                                    129089692,
                                    70986839,
                                    97257675,
                                    92789963,
                                    83000449,
                                    117543366,
                                    72098123,
                                    7786998
                                ]
                            },
                            "Z": {
                                "N": [
                                    1,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0
                                ]
                            }
                        }
                    },
                    "c": {
                        "Value": {
                            "X": {
                                "N": [
                                    20125623,
                                    20176707,
                                    37115545,
                                    29480970,
                                    20550743,
                                    52522447,
                                    8329405,
                                    21136545,
                                    65772732,
                                    2682882
                                ]
                            },
                            "Y": {
                                "N": [
                                    130247841,
                                    76848440,
                                    87866398,
                                    79822509,
                                    134045275,
                                    132632185,
                                    110300858,
                                    114693823,
                                    101800056,
                                    5145087
                                ]
                            },
                            "Z": {
                                "N": [
                                    1,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0,
                                    0
                                ]
                            }
                        }
                    }
                }
            },
            "KShare": {},
            "ChiShare": {}
        }
    ],
    "rawPreSignatures": [
        "pmJJRFggBmFIloUnbQKPzxY+BeA9/Jza76b+NqHj7VIaibjvNlhhUlghA56si8I3e0tWENN7jrD3bVBsjchhNLF9HaxGFExVCG/nZFJCYXJYcKNhYVghAhJZhVXREfIMZ7wyAf8YLlxhHjJui/t3TyFckDVSljhkYWJYIQIi5fy38P33g71f1tv2gGha5VyN4socDlvCzHhOTVG/BWFjWCEDTUZUQXoDqXLXCAg0+744lowXb1AUNS867SEL1F9s3L9hU1hwo2FhWCECaxl+C6AkK0RdTNDhNVKoUJ68g84Bhvu0tR76Oc20O1thY1ghAqPAC+ucvFChKEfxi9yFtz05lFdwdgKjZWmUz30NMxe3YWJYIQO70Bg7nfLolPXf1uefPPf/SSA3XdRCOMNEMzMq19v9NGZLU2hhcmVYIBE4sKejN2RN33JuuLcFqUsG+LJCaYMhWLHD0mXdl2D2aENoaVNoYXJlWCCDm7m3CetwETwA0CGlUjWQaxYnP4nvjt7Bu75widNbkg==",
        "pmJJRFggBmFIloUnbQKPzxY+BeA9/Jza76b+NqHj7VIaibjvNlhhUlghA56si8I3e0tWENN7jrD3bVBsjchhNLF9HaxGFExVCG/nZFJCYXJYcKNhYlghAiLl/Lfw/feDvV/W2/aAaFrlXI3iyhwOW8LMeE5NUb8FYWFYIQISWYVV0RHyDGe8MgH/GC5cYR4ybov7d08hXJA1UpY4ZGFjWCEDTUZUQXoDqXLXCAg0+744lowXb1AUNS867SEL1F9s3L9hU1hwo2FiWCEDu9AYO53y6JT139bnnzz3/0kgN13UQjjDRDMzKtfb/TRhY1ghAqPAC+ucvFChKEfxi9yFtz05lFdwdgKjZWmUz30NMxe3YWFYIQJrGX4LoCQrRF1M0OE1UqhQnryDzgGG+7S1Hvo5zbQ7W2ZLU2hhcmVYILkpR+f2SKUQvasS2mjnhrWjhAiXjSesysYGPaWFtBaJaENoaVNoYXJlWCCfllFdCMdEBgOAcTqTM7LwVrm36fv4vZXc9XkVeHD0Aw==",
        "pmJJRFggBmFIloUnbQKPzxY+BeA9/Jza76b+NqHj7VIaibjvNlhhUlghA56si8I3e0tWENN7jrD3bVBsjchhNLF9HaxGFExVCG/nZFJCYXJYcKNhYVghAhJZhVXREfIMZ7wyAf8YLlxhHjJui/t3TyFckDVSljhkYWJYIQIi5fy38P33g71f1tv2gGha5VyN4socDlvCzHhOTVG/BWFjWCEDTUZUQXoDqXLXCAg0+744lowXb1AUNS867SEL1F9s3L9hU1hwo2FjWCECo8AL65y8UKEoR/GL3IW3PTmUV3B2AqNlaZTPfQ0zF7dhYVghAmsZfgugJCtEXUzQ4TVSqFCevIPOAYb7tLUe+jnNtDtbYWJYIQO70Bg7nfLolPXf1uefPPf/SSA3XdRCOMNEMzMq19v9NGZLU2hhcmVYIMhzx3nBlYS8YWn7CJHu2AehNmJrhCcBmRWwGsznQNNraENoaVNoYXJlWCCrl5xbB1NI8lwHTByRNfFZTc2VXmj7/0q/uridkATXZA=="
    ]

    }
    headers = {
        'Authorization': '', 
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers, data=json.dumps(payload))
    return jsonify(response.json()) 
    #Final Signatures Should Match Across Different Parties



@blueprint.route('/xrpl/generate-bip39-mnemonic')
def generate_seed():
    m = Mnemonic("english")
    words = m.generate(strength=160)  # 160 bits of entropy gives 15 words
    mnemonic_bip_39_seed = words
    cipher = cipher_suite.encrypt(mnemonic_bip_39_seed.encode()).decode()
    return {"seed": mnemonic_bip_39_seed, "cipher": cipher, "encryption_key": one_time_encryption_key}

@blueprint.route('/xrpl/generate-bip42-xpub')
def create_extended_public_key(network = "XRP", seed = None, internal = False):
    seed_bytes = generate_seed()['seed'] #Example usage with a new XPUB
    if network == "XRP":
        bip_obj_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.RIPPLE)

        if internal:
            return jsonify({"xpub": bip_obj_mst.PublicKey().ToExtended()})
        else:
            return {"xpub": bip_obj_mst.PublicKey().ToExtended()}

    return jsonify({"error": "Unsupported network"})  

@blueprint.route('/xrpl/create_wallet')
def create_wallet():
    wallet = Wallet.create()
    return jsonify({"public_key": wallet.public_key, "classic_address":wallet.classic_address, "private_key": wallet.private_key})

@blueprint.route('/xrpl/generate-wallet-by-index')
def create_account_by_index(idx = 2):
    SEED = generate_seed()['seed']
    SEED_BYTES = Bip39SeedGenerator(SEED).Generate()
    bip44_ctx = Bip44.FromSeed(SEED_BYTES, Bip44Coins.RIPPLE)
    bip44_addr_ctx = bip44_ctx.Purpose().Coin().Account(idx).Change(Bip44Changes.CHAIN_EXT)
    classic_address = bip44_addr_ctx.PublicKey().ToAddress()
    public_key = bip44_addr_ctx.PublicKey().RawCompressed().__str__().upper()
    private_key = bip44_addr_ctx.PrivateKey().Raw().__str__().upper()
    return jsonify({"public_key": classic_address, "classic_address":public_key, "private_key": private_key})

@blueprint.route('/xrpl/check_address_balance')
def check_address_balance(address = "rNxp4h8apvRis6mJf9Sh8C6iRxfrDWN7AV"):
    balance = xrpl.account.get_balance(address, CLIENT)
    return jsonify({"balance": balance, "formatted_balance": balance / 10 ** 6})



@blueprint.route('/send_webhook')
def webhook_example(payload = {"address": "example"}, url = "https://webhook.site/af38e35c-d793-4daa-9a27-511122e8b0cf"):
    data = payload
    send_webhook(url = "https://webhook.site/af38e35c-d793-4daa-9a27-511122e8b0cf", payload = data)
    return {"Message": "Webhook Sent", "Data": data}


@blueprint.route('/xrpl/sss-keyshares/<parties>/<recovery>')
@blueprint.route('/xrpl/sss-keyshares')
def shamir_secret_sharing(network = "XRP", parties = 3, recovery = 2, internal = False):
    def generate_shares(secret, n, k):
        secret_bytes = secret.encode('utf-8')
        chunks = [secret_bytes[i : i + 16] for i in range(0, len(secret_bytes), 16)]
        shares = [list(Shamir.split(k, n, int.from_bytes(chunk, 'big'))) for chunk in chunks]
        transposed_shares = list(zip(*shares))
        # Convert shares to hexadecimal strings
        hex_shares = [[(x, hexlify(y).decode()) for x, y in share] for share in transposed_shares]
        return hex_shares
    shares = generate_shares(generate_seed()['seed'], int(parties), int(recovery))
    if internal:
        return shares 
    else:
        return jsonify(shares)
    return "200"



@blueprint.route('/xrpl/sss-recovery')
def shard_recovery(shares = None):
    shares = shamir_secret_sharing(internal = True)
    int_shares = [[(x, unhexlify(y)) for x, y in share] for share in shares]
    shares_by_chunk = list(zip(*int_shares))
    secret_chunks = [Shamir.combine(chunk_shares) for chunk_shares in shares_by_chunk]
    secret = b''.join(chunk for chunk in secret_chunks)
    try:
        secret = secret.decode('utf-8')
    except UnicodeDecodeError:
        secret = {"recovered_secret": hexlify(secret).decode()}
    return secret


@blueprint.route('/xrpl/generate-address-from-xpub')
def generate_address_from_xpub(xpub = None):
    def derive_xrp_address(xpub, index=0):
        bip32_wallet = BIP32.from_xpub(xpub)
        pubkey = bip32_wallet.get_pubkey_from_path(f"m/{index}")
        print(pubkey)
        return public_key_to_xrpl_address(pubkey.hex())

    xpub = create_extended_public_key()['xpub']
    index = 0  # or any other index for the child key you wish to derive
    address = derive_xrp_address(xpub, index)
    return {"address": address, "xpub": str(xpub), "index": index}





@blueprint.route('/xrpl/broadcast_transaction')
def broadcast_xrpl_transaction(xpub = None):
    testnet_url = "https://s.altnet.rippletest.net:51234/"
    client = JsonRpcClient(testnet_url)
    
    # Generate a wallet on the Testnet
    from_wallet = generate_faucet_wallet(client, debug=True)
    
    # Specify the recipient's address
    to_address = "rQav2te8UxscYC66jQgkfNB2cNN5PiSgaR"
    
    # Specify the amount to send (in XRP, not drops)
    amount = "22.123"  # Send 22.123 XRP

    # Send the transaction
    transaction_response = send_xrpl_transaction(from_wallet, to_address, amount, client)
    return jsonify(transaction_response)


def send_xrpl_transaction(from_wallet: Wallet, to_address: str, amount: str, client: JsonRpcClient):
    # Create a payment transaction
    a = int(decimal.Decimal(amount) * 10 ** 6)
    my_payment = Payment(
        account=from_wallet.classic_address,
        destination=to_address,
        amount=str(a),
    )

    # Autofill and sign the transaction
    signed_tx = autofill_and_sign(my_payment, client, from_wallet)

    # Submit the transaction
    response = submit_and_wait(signed_tx, client)

    # Return the response
    return response



@blueprint.route('/xrpl/fernet_encryption')
def fernet_helper():
    return {"encryption_key": str(Fernet.generate_key().decode())}



@blueprint.route('/xrpl/get-transactions')
def fetch_transactions(address="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"):
    response = CLIENT.request(AccountTx(account=address))
    transactions = response.result["transactions"]
    payment_transactions = [tx for tx in transactions if tx["tx"]["TransactionType"] == "Payment"]
    return jsonify(payment_transactions)


XRP_ALPHABET = 'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'

def b58encode_xrp(data):
    """Encode bytes into a base58-encoded string with XRP alphabet."""
    b58_digits = XRP_ALPHABET

    # Convert big-endian bytes to integer
    n = int.from_bytes(data, 'big')

    # Divide that integer into base58
    res = []
    while n > 0:
        n, idx = divmod(n, 58)
        res.append(b58_digits[idx])
    res = ''.join(res[::-1])

    # Encode leading zeros as base58 zeros
    czero = 0
    pad = 0
    for c in data:
        if c == czero:
            pad += 1
        else:
            break
    return b58_digits[0] * pad + res

def public_key_to_xrpl_address(public_key_hex):
    public_key = bytes.fromhex(public_key_hex)

    # 1. Compute the SHA-256 hash of the public key.
    sha256_hash = hashlib.sha256(public_key).digest()

    # 2. Compute the RIPEMD-160 hash of the SHA-256 hash.
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    # 3. Prepend the version byte 0x00 to the RIPEMD-160 hash.
    version_byte = b'\x00'
    payload = version_byte + ripemd160_hash

    # 4. Double SHA-256 hash and take the first 4 bytes as a checksum.
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

    # 5. Append the checksum to the result.
    full_payload = payload + checksum

    # 6. Base58 encode the result using the XRP Ledger alphabet.
    xrpl_address = b58encode_xrp(full_payload)

    return xrpl_address



def mnemonic_to_int(mnemonic: str) -> int:
    words = mnemonic.split(" ")
    num = 0
    for word in words:
        num = (num << 11) + word_to_int_dict[word]  # Shift the number 11 bits to the left and add the current word's integer representation
    return num

def int_to_mnemonic(secret: int) -> str:
    words = []
    while secret > 0:
        words.append(int_to_word_dict[secret & 0x7FF])  # Get the last 11 bits and convert them to a word
        secret = secret >> 11  # Shift the secret 11 bits to the right
    return " ".join(reversed(words))  # Join the words in reverse order

def share_to_private_key(share):
    x, y = share
    combined = str(x) + str(y)
    hashed = hashlib.sha256(combined.encode()).digest()
    private_key = hashed[:32]  # Take the first 32 bytes
    return private_key

def split_shares(secret: int, num_shares: int, threshold: int) -> List[Tuple[str, str]]:
    prime = 2**127 - 1  # Prime number used for finite field arithmetic
    shares = []
    
    # Generate random coefficients for the polynomial
    coefficients = [randbits(128) % prime for _ in range(threshold - 1)]
    
    for i in range(1, num_shares + 1):
        x = randbits(128) % prime
        y = secret
        
        # Evaluate the polynomial at x to get the share
        for j, coefficient in enumerate(coefficients, start=1):
            y += coefficient * (x ** j)
        
        # Convert x and y to mnemonic strings before adding them to the shares list
        shares.append((int_to_mnemonic(x), int_to_mnemonic(y % prime)))
    
    return shares

def recompute_secret(shares: List[Tuple[str, str]], threshold: int) -> str:
    prime = 2**127 - 1  # Prime number used for finite field arithmetic
    secret = 0
    
    for i in range(threshold):
        xi_mnemonic, yi_mnemonic = shares[i]
        xi = mnemonic_to_int(xi_mnemonic)
        yi = mnemonic_to_int(yi_mnemonic)
        numerator = 1
        denominator = 1
        
        # Compute the Lagrange basis polynomials
        for j in range(threshold):
            if i != j:
                xj_mnemonic, _ = shares[j]
                xj = mnemonic_to_int(xj_mnemonic)
                numerator = (numerator * (-xj)) % prime
                denominator = (denominator * (xi - xj)) % prime
        
        # Add the share to the reconstructed secret
        secret = (secret + (yi * numerator * pow(denominator, prime - 2, prime))) % prime
    
    reconstructed_mnemonic = int_to_mnemonic(secret)
    return reconstructed_mnemonic


def shamir_secret_sharing_shard_generation(parties=2, threshold=2):
    mnemonic_bip_39_seed = generate_seed()['seed']
    secret = mnemonic_to_int(mnemonic_bip_39_seed)
    num_shares = parties
    threshold = threshold


    shares = generate_shares(secret, num_shares, threshold)
    mnemonic = reconstruct_secret(shares)


    shard_encryption = cipher_suite.encrypt(json.dumps(shares).encode()).decode()
    return {"shards": shares, "mpc_mnemonic": mnemonic, "encrypted_shards": shard_encryption, "encryption_key": one_time_encryption_key, "seed": mnemonic_bip_39_seed}


@blueprint.route('/smpc_shamir_shards')
def shamir_secret_sharing_shard_generation(parties=3, threshold=2):
    m = Mnemonic("english")
    words = m.generate(strength=128)  # 128 bits of entropy gives 12 words
    mnemonic_bip_39_seed = words
    secret = mnemonic_to_int(mnemonic_bip_39_seed)
    num_shares = parties
    threshold = threshold
    shares = split_shares(secret, num_shares, threshold)
    reconstructed_mnemonic = recompute_secret([shares[0], shares[1]], threshold)
    shard_encryption = cipher_suite.encrypt(json.dumps(shares).encode()).decode()
    return {"shards": shares, "encrypted_shards": shard_encryption, "encryption_key": one_time_encryption_key, "seed": mnemonic_bip_39_seed}    

@blueprint.route('/smpc_computation/<key>/<encrypted_shards>')
def recompute_shared_secret_smpc(key, encrypted_shards):
    encrypted_shards_bytes = encrypted_shards.encode('utf-8')
    encrypted_shards_decoded = cipher_suite.decrypt(encrypted_shards_bytes)

    # Convert the decrypted shards to a list
    decrypted_shards = json.loads(encrypted_shards_decoded)
    print(decrypted_shards)

    def recompute_secret(shares: List[Tuple[str, str]], threshold: int) -> str:
        prime = 2**127 - 1  # Prime number used for finite field arithmetic
        secret = 0
        
        for i in range(threshold):
            xi_mnemonic, yi_mnemonic = shares[i]
            xi = mnemonic_to_int(xi_mnemonic)
            yi = mnemonic_to_int(yi_mnemonic)
            numerator = 1
            denominator = 1
            
            # Compute the Lagrange basis polynomials
            for j in range(threshold):
                if i != j:
                    xj_mnemonic, _ = shares[j]
                    xj = mnemonic_to_int(xj_mnemonic)
                    numerator = (numerator * (-xj)) % prime
                    denominator = (denominator * (xi - xj)) % prime
            # Add the share to the reconstructed secret
            secret = (secret + (yi * numerator * pow(denominator, prime - 2, prime))) % prime
        
        reconstructed_mnemonic = int_to_mnemonic(secret)
        return reconstructed_mnemonic
    recomputed_secret = recompute_secret(decrypted_shards, threshold = 2)

    return {"decrypted_shards": decrypted_shards, "private_key": recomputed_secret}

@blueprint.route('/generate_bip_44_address/<key>/<encrypted_shards>')
def generate_bip_44_address(key, encrypted_shards):
    #SEED = recompute_shared_secret_smpc(key = key,encrypted_shards=encrypted_shards)['private_key']
    SEED = "travel slice body volume story quiz rose pretty tide toss other author gift pattern empower"
    def _account_by_index(self, idx: int) -> Wallet:
        SEED_BYTES = Bip39SeedGenerator(SEED).Generate()
        bip44_ctx = Bip44.FromSeed(SEED_BYTES, Bip44Coins.RIPPLE)
        bip44_addr_ctx = bip44_ctx.Purpose().Coin().Account(idx).Change(Bip44Changes.CHAIN_EXT)
        wallet = Wallet.create()
        wallet.classic_address = bip44_addr_ctx.PublicKey().ToAddress()
        wallet.public_key = bip44_addr_ctx.PublicKey().RawCompressed().__str__().upper()
        wallet.private_key = bip44_addr_ctx.PrivateKey().Raw().__str__().upper()
        wallet.seed = ""
        print(wallet)
        return wallet

    xrp_address = (_account_by_index(SEED, 1))
    return {"wallet": xrp_address.address}



@blueprint.route('/generate-address')
def generate_address():
    url = "https://www.poof.io/api/v2/create_charge"
    payload = {
        "amount": "2",
        "crypto": "xrp"
    }
    headers = {
        "Authorization": "uVizoJ_VF7tOxef8PXhp3Q",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers).json()
    response['destination_tag'] = response['uuid']
    return response

@blueprint.route('/generate_invoice')
def generate_xrp_invoice():
    url = "https://www.poof.io/api/v2/create_invoice"
    payload = {
        "amount": "2",
        "crypto": "xrp"
    }
    headers = {
        "Authorization": "uVizoJ_VF7tOxef8PXhp3Q",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@blueprint.route('/fetch-price')
def fetch_xrp_price():

    url = "https://www.poof.io/api/v2/price"

    payload = {"crypto": "xrp"}
    headers = {
        "Authorization": "uVizoJ_VF7tOxef8PXhp3Q",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'accounts/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Email already registered', 
                                    success=False,
                                    form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template( 'accounts/register.html', 
                                msg='User created please <a href="/login">login</a>', 
                                success=True,
                                form=create_account_form)

    else:
        return render_template( 'accounts/register.html', form=create_account_form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
