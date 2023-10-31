import psycopg2
from app import db
from app.base.models import User, xrp
import json

import xrpl.account
from bip_utils import *
from typing import Union, Tuple

from mnemonic import Mnemonic
from xrpl.account import get_next_valid_seq_number
from xrpl.asyncio.clients import XRPLRequestFailureException
from xrpl.clients import JsonRpcClient
from xrpl.core import keypairs
from xrpl.core.binarycodec import encode_for_signing
from xrpl.core.keypairs import sign
from xrpl.ledger import get_fee, get_latest_validated_ledger_sequence
from xrpl.models import Payment, AccountDelete
from xrpl.transaction import safe_sign_transaction, send_reliable_submission, safe_sign_and_autofill_transaction
from xrpl.wallet import Wallet

import uuid
import datetime
import decimal
from cryptography.fernet import Fernet
import os

from config import config_dict
from decouple import config
import random

test_environment = config_dict['Production'.capitalize()].test_environment
if test_environment:
    SEED = "plug book blossom path green supreme tank ride coast world tongue profit actor blood tiger"
else:
    SEED = os.getenv('xrp_encryption').encode('UTF-8')
    decryption = os.getenv('encryption').encode('UTF-8')
    fernet = Fernet(decryption)
    SEED = fernet.decrypt(SEED).decode('UTF-8')

COINS = ['xrp']
RPC = "https://xrplcluster.com/"

def generate_uuid():
    return random.randint(0,999999999)



class Adapter:
    def __init__(self, coin):
        self.CLIENT = JsonRpcClient(RPC)

    def generate_address(self, coin) -> str:

        main_address = (self.main_address())
        """Generate an address and store it to the database as (id, address)"""
        try: 
            last_id_db = xrp.query.order_by(xrp.id.desc()).first().id
        except:
            last_id_db = None

        # If no id in db start with id 1, else increment the id by one to get a new and unused address
        if isinstance(last_id_db, int):
            last_id = last_id_db + 1
        else:
            last_id = 1

        wallet = self._account_by_index(last_id)
        address = wallet.classic_address

        uuid = generate_uuid()
        xrp_ledger = xrp(uuid = uuid, coin_type = "xrp", balance = "", address = str(main_address), transaction_hash = "", amount = "", original_amount = "", network_fee = "", fee="", fee_to = "", date = datetime.datetime.now(),checked = "", method = "" ,status = "",meta = "")
        db.session.add(xrp_ledger)
        db.session.commit()
        return main_address, str(uuid)

    def transaction(self, sender: str, recipient: str, amount: float):
        fee = int(get_fee(self.CLIENT))
        # Check if sender is main address or sub address stored in the db
        if sender == self.main_address():
            main = True
            wallet: Wallet = self._main_account()
        else:
            main = False
            wallet: Wallet = self._account_by_address(sender)

        # Format amount from float to xrp drops
        a = int(decimal.Decimal(amount) * 10 ** 6)
        if a - fee <= 0:
            raise Exception("Required fee is bigger than amount")
        famount = a- fee

        # Create transaction and broadcast it
        if main:
            tx = Payment(
                account=wallet.classic_address,
                amount=str(famount),
                destination=recipient,
            )
        else:
            tx = AccountDelete(
                account=wallet.classic_address,
                destination=recipient,
            )
        try:
            signed_tx = safe_sign_and_autofill_transaction(tx, wallet, self.CLIENT)
            resp = send_reliable_submission(signed_tx, self.CLIENT)
        except:
            raise Exception("Error while broadcasting transaction")

        return {
            'hash': resp.result['hash'],
            'amount': famount / 10 ** 6
        }

    def available_query_xrp(self, address, uuid):
        tsx_list = xrpl.account.get_account_transactions(str(self.main_address()), self.CLIENT)
        uuids = {}
        for i in tsx_list[0:10]:
            if 'tx' in i:
                if 'DestinationTag' in i['tx']:
                    xrp_tx = i['tx']
                    destination_tag = xrp_tx['DestinationTag']
                    if destination_tag:
                        destination_tag = str(destination_tag)
                    if destination_tag in uuid:
                        sender = xrp_tx['Account']
                        amount = decimal.Decimal(xrp_tx['Amount'])/(10 ** 6)
                        fee = decimal.Decimal(xrp_tx['Fee'])/(10 ** 6)
                        total_amount = decimal.Decimal(amount)-decimal.Decimal(fee)
                        uuids[destination_tag] = {"sender": sender,"transaction_hash": transaction_hash, "network_fee": str(fee), "amount": str(total_amount), "original_amount": str(amount)}
        return uuids

    def available_balance(self, address: str):
        try:
            balance = xrpl.account.get_balance(address, self.CLIENT)
        except XRPLRequestFailureException:
            return 0

        return balance / 10 ** 6

    def main_address(self) -> str:
        return self._account_by_index(0).classic_address

    def _main_account(self) -> Wallet:
        return self._account_by_index(0)

    def _account_by_index(self, idx: int) -> Wallet:
        SEED_BYTES = Bip39SeedGenerator(SEED).Generate()
        bip44_ctx = Bip44.FromSeed(SEED_BYTES, Bip44Coins.RIPPLE)
        bip44_addr_ctx = bip44_ctx.Purpose().Coin().Account(idx).Change(Bip44Changes.CHAIN_EXT)
        wallet = Wallet.create()
        wallet.classic_address = bip44_addr_ctx.PublicKey().ToAddress()
        wallet.public_key = bip44_addr_ctx.PublicKey().RawCompressed().__str__().upper()
        wallet.private_key = bip44_addr_ctx.PrivateKey().Raw().__str__().upper()
        wallet.seed = ""
        return wallet

    def _account_by_address(self, address: str) -> Wallet:
        """Check if an address is in the database and return it as account"""
        db_query = xrp.query.filter(xrp.address == address).first()
        if not db_query:
            raise Exception("Address not found in the database")
        return self._account_by_index(db_query.id)