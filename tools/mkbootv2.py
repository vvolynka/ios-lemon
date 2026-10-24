#!/usr/bin/env python3
"""Create an Android boot image v2."""
import argparse, struct, os

def parse_os_version(s):
    return 0x170000

def parse_patch_level(s):
    return 0

def main():
    ap = argparse.ArgumentParser(description="Create Android boot.img v2")
    ap.add_argument('--kernel', required=True)
    ap.add_argument('--ramdisk', required=True)
    ap.add_argument('--dtb', required=True)
    ap.add_argument('--base', type=lambda x: int(x, 0), default=0)
    ap.add_argument('--kernel_offset', type=lambda x: int(x, 0), default=0x8000)
    ap.add_argument('--ramdisk_offset', type=lambda x: int(x, 0), default=0x1000000)
    ap.add_argument('--tags_offset', type=lambda x: int(x, 0), default=0x100)
    ap.add_argument('--dtb_offset', type=lambda x: int(x, 0), default=0x1f00000)
    ap.add_argument('--pagesize', type=lambda x: int(x, 0), default=4096)
    ap.add_argument('--os_version', default='17.0.0')
    ap.add_argument('--os_patch_level', default='2035-06')
    ap.add_argument('--cmdline', default='console=null')
    ap.add_argument('-o', '--output', required=True)
    a = ap.parse_args()

    kernel_data = open(a.kernel, 'rb').read()
    ramdisk_data = open(a.ramdisk, 'rb').read()
    dtb_data = open(a.dtb, 'rb').read()

    ps = a.pagesize
    rnd = lambda n: (n + ps - 1) // ps * ps

    header = bytearray(ps)
    # Magic
    header[0:8] = b'ANDROID!'
    
    ks = len(kernel_data)
    ka = a.base + a.kernel_offset
    rs = len(ramdisk_data)
    ra = a.base + a.ramdisk_offset
    ss = 0
    sa = 0
    ta = a.base + a.tags_offset
    
    osv = parse_os_version(a.os_version) | (parse_patch_level(a.os_patch_level) << 25)

    struct.pack_into('<10I', header, 8, ks, ka, rs, ra, ss, sa, ta, ps, 2, osv)

    # Name (16 bytes)
    # Cmdline (512 bytes)
    cmdline_bytes = a.cmdline.encode()[:512]
    header[64:64+len(cmdline_bytes)] = cmdline_bytes

    # v1/v2 specific fields
    # at offset 1632: rds, rdo, hs
    # at offset 1648: ds, da
    # Let's compute offsets
    off = ps
    kernel_off = off
    off += rnd(ks)
    ramdisk_off = off
    off += rnd(rs)
    dtb_off = off
    off += rnd(len(dtb_data))

    header_size = ps # version 2 header size = 1660 packed to page size
    struct.pack_into('<IQI', header, 1632, 0, 0, header_size)
    struct.pack_into('<IQ', header, 1648, len(dtb_data), a.base + a.dtb_offset)

    out = bytearray()
    out += header
    out += kernel_data + b'\0' * (rnd(ks) - ks)
    out += ramdisk_data + b'\0' * (rnd(rs) - rs)
    out += dtb_data + b'\0' * (rnd(len(dtb_data)) - len(dtb_data))

    open(a.output, 'wb').write(out)
    print(f'Successfully created {a.output} ({len(out)} bytes)')

if __name__ == '__main__':
    main()
