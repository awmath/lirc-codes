#!/usr/bin/env python3
import binascii


def pronto2lirc(pronto):
    codes = [int(binascii.hexlify(pronto[i:i+2]), 16) for i in range(0, len(pronto), 2)]

    if codes[0]:
        raise ValueError('Pronto code should start with 0000')
    if len(codes) != 4 + 2 * (codes[2] + codes[3]):
        raise ValueError('Number of pulse widths does not match the preamble')

    frequency = 1 / (codes[1] * 0.241246)
    return [int(round(code / frequency)) for code in codes[4:]]


if __name__ == '__main__':
    import sys

    for code in sys.argv[1:]:
        pronto = bytearray.fromhex(code)
        pulses = pronto2lirc(pronto)

        print(pulses)