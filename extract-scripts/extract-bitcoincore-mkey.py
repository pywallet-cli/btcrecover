#!/usr/bin/env python

# extract-bitcoincore-mkey.py -- Bitcoin wallet master key extractor
# Copyright (C) 2014, 2015 Christopher Gurnee
#
# This file is part of btcrecover.
#
# btcrecover is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#
# btcrecover is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/

import sys, os.path, bsddb3.db, struct, base64, zlib

prog = os.path.basename(sys.argv[0])

if len(sys.argv) != 2 or sys.argv[1].startswith("-"):
    print("usage:", prog, "BITCOINCORE_WALLET_FILE", file=sys.stderr)
    sys.exit(2)

wallet_filename = os.path.abspath(sys.argv[1])

with open(wallet_filename, "rb") as wallet_file:
    wallet_file.seek(12)
    if wallet_file.read(8) != b"\x62\x31\x05\x00\x09\x00\x00\x00":  # BDB magic, Btree v9
        print(prog+": error: file is not a Bitcoin Core wallet", file=sys.stderr)
        sys.exit(1)

db_env = bsddb3.db.DBEnv()
db_env.open(os.path.dirname(wallet_filename), bsddb3.db.DB_CREATE | bsddb3.db.DB_INIT_MPOOL)
db = bsddb3.db.DB(db_env)
db.open(wallet_filename, "main", bsddb3.db.DB_BTREE, bsddb3.db.DB_RDONLY)
mkey = db.get(b"\x04mkey\x01\x00\x00\x00")
db.close()
db_env.close()

if not mkey:
    raise ValueError("Encrypted master key #1 not found in the Bitcoin Core wallet file.\n"+
                     "(is this wallet encrypted? is this a standard Bitcoin Core wallet?)")

# This is a little fragile because it assumes the encrypted key and salt sizes are
# 48 and 8 bytes long respectively, which although currently true may not always be:
# (it will loudly fail if this isn't the case; if smarter it could gracefully succeed):
encrypted_master_key, salt, method, iter_count = struct.unpack_from("< 49p 9p I I", mkey)
if method != 0:
    print(prog+": warning: unexpected Bitcoin Core key derivation method", str(method), file=sys.stderr)

print("Partial Bitcoin Core encrypted master key, salt, iter_count, and crc in base64:", file=sys.stderr)

# Only include the last two AES blocks (last 32 bytes) of the 48-byte encrypted master key
bytes = b"bc:" + encrypted_master_key[-32:] + salt + struct.pack("<I", iter_count)
crc_bytes = struct.pack("<I", zlib.crc32(bytes) & 0xffffffff)

print(base64.b64encode(bytes + crc_bytes).decode())
