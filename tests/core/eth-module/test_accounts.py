# coding=utf-8

from __future__ import unicode_literals

import pytest
import sys

from eth_utils import (
    is_address,
    is_hex,
)

from web3.utils.encoding import (
    to_hex,
)


def to_hex_if_py2(val):
    if sys.version_info.major < 3:
        return to_hex(val)
    else:
        return val


@pytest.fixture
def PRIVATE_BYTES():
    key = b'unicorns' * 4
    return to_hex_if_py2(key)


@pytest.fixture
def PRIVATE_BYTES_ALT(PRIVATE_BYTES):
    key = b'rainbows' * 4
    return to_hex_if_py2(key)


def test_eth_account_create_variation(web3):
    account1 = web3.eth.account.create()
    account2 = web3.eth.account.create()
    assert account1 != account2


def test_eth_account_privateKeyToAccount_reproducible(web3, PRIVATE_BYTES):
    account1 = web3.eth.account.privateKeyToAccount(PRIVATE_BYTES)
    account2 = web3.eth.account.privateKeyToAccount(PRIVATE_BYTES)
    assert bytes(account1) == PRIVATE_BYTES
    assert bytes(account1) == bytes(account2)


def test_eth_account_privateKeyToAccount_diverge(web3, PRIVATE_BYTES, PRIVATE_BYTES_ALT):
    account1 = web3.eth.account.privateKeyToAccount(PRIVATE_BYTES)
    account2 = web3.eth.account.privateKeyToAccount(PRIVATE_BYTES_ALT)
    assert bytes(account2) == PRIVATE_BYTES_ALT
    assert bytes(account1) != bytes(account2)


def test_eth_account_privateKeyToAccount_seed_restrictions(web3):
    with pytest.raises(ValueError):
        web3.eth.account.privateKeyToAccount(b'')
    with pytest.raises(ValueError):
        web3.eth.account.privateKeyToAccount(b'\xff' * 31)
    with pytest.raises(ValueError):
        web3.eth.account.privateKeyToAccount(b'\xff' * 33)


def test_eth_account_privateKeyToAccount_properties(web3, PRIVATE_BYTES):
    account = web3.eth.account.privateKeyToAccount(PRIVATE_BYTES)
    assert callable(account.sign)
    assert callable(account.signTransaction)
    assert is_address(account.address)
    assert account.address == '0xa79F6f349C853F9Ea0B29636779ae3Cb4E3BA729'
    assert account.privateKey == PRIVATE_BYTES


def test_eth_account_create_properties(web3):
    account = web3.eth.account.create()
    assert callable(account.sign)
    assert callable(account.signTransaction)
    assert is_address(account.address)
    if sys.version_info.major < 3:
        assert is_hex(account.privateKey) and len(account.privateKey) == 66
    else:
        assert isinstance(account.privateKey, bytes) and len(account.privateKey) == 32


def test_eth_account_recover_transaction_example(web3):
    raw_tx_hex = '0xf8640d843b9aca00830e57e0945b2063246f2191f18f2675cedb8b28102e957458018025a00c753084e5a8290219324c1a3a86d4064ded2d15979b1ea790734aaa2ceaafc1a0229ca4538106819fd3a5509dd383e8fe4b731c6870339556a5c06feb9cf330bb'  # noqa: E501
    from_account = web3.eth.account.recoverTransaction(raw_tx_hex)
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


def test_eth_account_recover_transaction_with_literal(web3):
    raw_tx = 0xf8640d843b9aca00830e57e0945b2063246f2191f18f2675cedb8b28102e957458018025a00c753084e5a8290219324c1a3a86d4064ded2d15979b1ea790734aaa2ceaafc1a0229ca4538106819fd3a5509dd383e8fe4b731c6870339556a5c06feb9cf330bb  # noqa: E501
    from_account = web3.eth.account.recoverTransaction(raw_tx)
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


def test_eth_account_recover_signature_bytes(web3):
    signature_bytes = b'\x0cu0\x84\xe5\xa8)\x02\x192L\x1a:\x86\xd4\x06M\xed-\x15\x97\x9b\x1e\xa7\x90sJ\xaa,\xea\xaf\xc1"\x9c\xa4S\x81\x06\x81\x9f\xd3\xa5P\x9d\xd3\x83\xe8\xfeKs\x1chp3\x95V\xa5\xc0o\xeb\x9c\xf30\xbb\x00'  # noqa: E501
    msg_hash = b'\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1'  # noqa: E501
    signature = to_hex_if_py2(signature_bytes)
    from_account = web3.eth.account.recover(msg_hash, signature=signature)
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


def test_eth_account_recover_vrs(web3):
    v, r, s = (
        27,
        5634810156301565519126305729385531885322755941350706789683031279718535704513,
        15655399131600894366408541311673616702363115109327707006109616887384920764603,
    )
    msg_hash = b'\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1'  # noqa: E501
    from_account = web3.eth.account.recover(msg_hash, vrs=(v, r, s))
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


def test_eth_account_recover_vrs_standard_v(web3):
    v, r, s = (
        0,
        5634810156301565519126305729385531885322755941350706789683031279718535704513,
        15655399131600894366408541311673616702363115109327707006109616887384920764603,
    )
    msg_hash = b'\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1'  # noqa: E501
    from_account = web3.eth.account.recover(msg_hash, vrs=(v, r, s))
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


@pytest.mark.parametrize(
    'message, expected',
    [
        (
            'Message tö sign. Longer than hash!',
            '0x10c7cb57942998ab214c062e7a57220a174aacd80418cead9f90ec410eacada1',
        ),
        (
            # Intentionally sneaky: message is a hexstr interpreted as text
            '0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821',
            '0x6192785e9ad00100e7332ff585824b65eafa30bc8f1265cf86b5368aa3ab5d56',
        ),
        (
            'Hello World',
            '0xa1de988600a42c4b4ab089b619297c17d53cffae5d5120d82d8a92d0bb3b78f2',
        ),
    ]
)
def test_eth_account_hash_message_text(web3, message, expected):
    assert web3.eth.account.hashMessage(text=message) == expected


@pytest.mark.parametrize(
    'message, expected',
    [
        (
            '0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821',
            '0x10c7cb57942998ab214c062e7a57220a174aacd80418cead9f90ec410eacada1',
        ),
        (
            '0x29d9f7d6a1d1e62152f314f04e6bd4300ad56fd72102b6b83702869a089f470c',
            '0xe709159ef0e6323c705786fc50e47a8143812e9f82f429e585034777c7bf530b',
        ),
    ]
)
def test_eth_account_hash_message_hexstr(web3, message, expected):
    assert web3.eth.account.hashMessage(hexstr=message) == expected


@pytest.mark.parametrize(
    'message, key, expected_bytes, expected_hash, v, r, s, signature',
    (
        (
            'Some data',
            '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318',
            b'Some data',
            '0x1da44b586eb0729ff70a73c326926f6ed5a25f5b056e7f47fbc6e58d86871655',
            28,
            '0xb91467e570a6466aa9e9876cbcd013baba02900b8979d43fe208a4a4f339f5fd',
            '0x6007e74cd82e037b800186422fc2da167c747ef045e5d18a5f5d4300f8e1a029',
            '0xb91467e570a6466aa9e9876cbcd013baba02900b8979d43fe208a4a4f339f5fd6007e74cd82e037b800186422fc2da167c747ef045e5d18a5f5d4300f8e1a0291c',  # noqa: E501
        ),
    ),
)
def test_eth_account_sign(web3, message, key, expected_bytes, expected_hash, v, r, s, signature):
    signed = web3.eth.account.sign(message_text=message, private_key=key)
    assert signed.message == expected_bytes
    assert signed.messageHash == expected_hash
    assert signed.v == v
    assert signed.r == r
    assert signed.s == s
    assert signed.signature == signature

    account = web3.eth.account.privateKeyToAccount(key)
    assert account.sign(message_text=message) == signed


@pytest.mark.parametrize(
    'txn, private_key, expected_raw_tx, tx_hash, r, s, v',
    (
        (
            {
                'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                'value': 1000000000,
                'gas': 2000000,
                'gasPrice': 234567897654321,
                'nonce': 0,
                'chainId': 1
            },
            '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318',
            '0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428',  # noqa: E501
            '0x6893a6ee8df79b0f5d64a180cd1ef35d030f3e296a5361cf04d02ce720d32ec5',
            '0x09ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9c',
            '0x440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428',
            37,
        ),
    ),
)
def test_eth_account_sign_transaction(web3, txn, private_key, expected_raw_tx, tx_hash, r, s, v):
    signed = web3.eth.account.signTransaction(txn, private_key)
    assert signed.hash == tx_hash
    assert signed.r == r
    assert signed.s == s
    assert signed.v == v
    assert signed.rawTransaction == expected_raw_tx

    account = web3.eth.account.privateKeyToAccount(private_key)
    assert account.signTransaction(txn) == signed


def test_eth_account_encrypt(web3):
    private_key = '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318'
    encrypted = web3.eth.account.encrypt(private_key, 'test!')

    assert encrypted['address'] == '2c7536e3605d9c16a7a3d7b1898e529396a65c23'
    assert encrypted['version'] == 3

    decrypted_key = web3.eth.account.decrypt(encrypted, 'test!')

    assert to_hex(decrypted_key) == private_key
