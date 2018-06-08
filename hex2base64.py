#!/usr/bin/env python3
from binascii import b2a_base64, unhexlify
from sys import argv


def hex2base64(string):
    return b2a_base64(unhexlify(string)).decode('UTF-8')


if __name__ == '__main__':
    if len(argv) < 2:
        while True:
            hex_string = input('Bitte hex string ein geben:\n')
            print(hex2base64(hex_string))

    print(hex2base64(argv[1]))
