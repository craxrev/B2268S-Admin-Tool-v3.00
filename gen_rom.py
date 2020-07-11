#!/usr/bin/env python3

########################################################################################################
#
# Generate new custom rom file from an old one.
# usage: gen_rom.py config.rom config-new.rom
#
########################################################################################################


import sys
import re
import base64
import zlib


VERBOSE = True

to_mod = [
    'root:.SAGmAlKFZxWw:18454',
    'Admin:jQ5e1sWQKpXw6:18454',
]


def read_rom():

    from_path = sys.argv[1]

    rom = None
    try:
        from_file = open(from_path, 'r')
        rom = from_file.read()
    except FileNotFoundError as e:
        print('%s file not found!' % from_path)
        sys.exit(1)

    if rom is None:
        print('error reading from %s' % from_path)
        sys.exit(1)

    return rom


def extract_shadow(rom):

    matches = re.findall(r'<Shadow>\s+<Value\s.*>(.*)<\/Value>\s+<Size\s.*>.*<\/Size>\s+<\/Shadow>', rom)
    if len(matches) == 0:
        print('Connot find shadow file!')
        sys.exit(1)

    return matches[0]


def mod_shadow(shadow):

    gzp_shadow = base64.b64decode(shadow)
    dec_shadow = zlib.decompress(gzp_shadow, 16+zlib.MAX_WBITS).decode('ascii')

    if VERBOSE:
        print('Before:')
        print(dec_shadow)

    for mod in to_mod:
        shadow_lines = mod.split(':')
        if (dec_shadow.find(shadow_lines[0]) == -1):
            print('could not find user "%s" in shadow file, aborting..' % shadow_lines[0])
            sys.exit(1)
        dec_shadow = re.sub((r'{}' + ':[^:]*' * (len(shadow_lines) - 1)).format(shadow_lines[0]), ('{}' + ':{}' * (len(shadow_lines) - 1)).format(*shadow_lines), dec_shadow)

    if VERBOSE:
        print('After:')
        print(dec_shadow)

    if dec_shadow.count(':') % 8 != 0:
        print('Error occured when generating the new shadow file, please verify code or something..')
        sys.exit(1)

    c_obj = zlib.compressobj(wbits=16+zlib.MAX_WBITS)
    gzp_new_shadow = c_obj.compress(dec_shadow.encode('ascii'))
    gzp_new_shadow += c_obj.flush()
    enc_new_shadow = base64.b64encode(gzp_new_shadow).decode('ascii')
    return enc_new_shadow


def gen_new_rom(rom, shadow):

    to_path = sys.argv[2]

    new_rom = re.sub(r'(<Shadow>\s+<Value\s.*>)(.*)(<\/Value>\s+<Size\s.*>)(.*)(<\/Size>\s+<\/Shadow>)', r'\g<1>{}\g<3>{}\g<5>'.format(shadow, len(shadow)), rom)

    if rom == new_rom:
        print('Nothing\'s changed, please check whatever\'s causing that!')
        sys.exit(1)

    if len(rom.split('\n')) != len(new_rom.split('\n')) and False:
        print('Error occured! Number of lines changed in the new rom file, please verify!')
        sys.exit(1)

    try:
        to_file = open(to_path, 'w')
        to_file.write(new_rom)
        to_file.close()
    except Execption as e:
        print('Error while writing new rom file!')
        sys.exit(1)


def main():

    if len(sys.argv) != 3:
        print('usage: gen_rom.py config.rom config-new.rom')
        sys.exit(0)

    if sys.argv[1] == sys.argv[2]:
        print('same input/output file, can\'t have that!')
        sys.exit(1)

    rom = read_rom()
    shadow = extract_shadow(rom)
    new_shadow = mod_shadow(shadow)
    gen_new_rom(rom, new_shadow)

    print('Done generating new modified rom, PLEASE make sure to check it manually before using it!')
    sys.exit(0)


if __name__ == '__main__':
    main()
