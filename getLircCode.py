#!/usr/bin/env python3
from argparse import ArgumentParser
from xml.dom import minidom
import urllib.request
from base64 import b64encode
from binascii import b2a_hex
from re import sub
from xml.sax.saxutils import escape
import struct


def lirc2broadlink(pulses):
    array = bytearray()

    for pulse in pulses:
        pulse = int(pulse * 269 / 8192)  # 32.84ms units
        if pulse < 256:
            array += bytearray(struct.pack('>B', pulse))  # big endian (1-byte)
        else:
            array += bytearray([0x00])  # indicate next number is 2-bytes
            array += bytearray(struct.pack('>H', pulse))  # big endian (2-bytes)

    packet = bytearray([0x26, 0x00])  # 0x26 = IR, 0x00 = no repeats
    packet += bytearray(struct.pack('<H', len(array)))  # little endian b   yte count
    packet += array
    packet += bytearray([0x0d, 0x05])  # IR terminator

    # Add 0s to make ultimate packet size a multiple of 16 for 128-bit AES encryption.
    remainder = (len(packet) + 4) % 16  # rm.send_data() adds 4-byte header (02 00 00 00)
    if remainder:
        packet += bytearray(16 - remainder)

    return packet


def get_remote_xml(vendor, model):
    raw_url = 'https://raw.githubusercontent.com/awmath/lirc-remotes/xml/{vendor}/{model}.xml'\
        .format(vendor=vendor, model=model)

    try:
        xml_string = urllib.request.urlopen(raw_url).read().decode()
        fixed_xml = sub(r'\"(.+?)\"', lambda s: escape(s.group()), xml_string)
        return minidom.parseString(fixed_xml)
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    parser = ArgumentParser(description='Get HEX or BASE64 code from lirc database.')
    parser.add_argument('vendor', type=str, help='The remote vendor')
    parser.add_argument('model', type=str, help='The remote model')
    parser.add_argument('-b', '--base64', action='store_true', help='Print IR code in base64 instead of HEX')

    args = parser.parse_args()

    xml_data = get_remote_xml(args.vendor, args.model)
    if not xml_data:
        print('Error while getting xml data.')
        exit(1)

    for code in xml_data.getElementsByTagName('code'):
        print('Code {0}'.format(code.getAttribute('name')))

        cleaned_code = code.getElementsByTagName('ccf')[0].firstChild.data

        lirc_code = []
        for part in cleaned_code.split(' '):
            lirc_code.append(int(part, 16))
        broadlink_code = lirc2broadlink(lirc_code)
        if args.base64:
            print(b64encode(broadlink_code).decode())
        else:
            print(b2a_hex(broadlink_code).decode())

    exit(0)

