import json
import os
import sys

from . import metainfos

BYTECODE    =   ""
(ABI, ADDRESS) = metainfos.load_abi_address("nft1155")

if __name__ == "__main__":
    print(ADDRESS)
    print(ABI)
