# ios-lemon

**Apple's iOS 16 running on a Redmi 9T NFC (lemon).**

This project ports Apple's open-source XNU kernel (xnu-8796, the iOS 16 generation) to the Xiaomi Redmi 9T NFC (`lemon`, Qualcomm SM6115 / Snapdragon 662). On top of it runs the **unmodified iOS 16.7.16 (20H392) userland of the iPhone X**: launchd, the system daemons, backboardd, SpringBoard and the stock apps.

Based on the architecture of [ios-sweet](https://github.com/dipa-studio/ios-sweet) (Redmi Note 10 Pro / SM7150), adapted for the SM6115 SoC.

> Experimental bring-up, not a usable phone OS. Installs into the `userdata` partition and **erases Android's user data**.

## Hardware: Redmi 9T NFC (lemon)

| Component | Specification |
|-----------|---------------|
| SoC | Qualcomm SM6115 (Snapdragon 662) |
| CPU | 4× Cortex-A73 @ 2.0 GHz + 4× Cortex-A53 @ 1.8 GHz (ARMv8-A, 64-bit) |
| GPU | Adreno 610 |
| RAM | 4/6 GB LPDDR4X |
| Display | 1080×2400 @60Hz, IPS LCD |
| Touch | Goodix / Focaltech (I²C or SPI) |
| Storage | UFS 2.1 or eMMC 5.1 |
| Bootloader | Unlockable (EDL mode) |

## Repository layout

| Path | What |
|------|------|
| `shim/` | Bare-metal boot shim (C + asm) packed as an Android boot.img v2 |
| `xnu/patches/` | XNU patch series (to be created), plus staging scripts |
| `tools/mkadt.py` | Generates the Apple Device Tree from lemon's MMIO layout |
| `tools/mkpayload.py` | Packs kernel + ADT + boot-args into the shim payload |
| `tools/mkiosroot.sh` | Builds the HFS+ iOS root from the IPSW images |
| `tools/lemon-root-tweaks.py` | Bring-up changes to the root (Setup skip, activation, daemons) |
| `tools/qemu-lemon.py` | QEMU test boots |

## Current status

**Kernel only** - initial bring-up phase. See `NOTES.md` for active work.

## How to build (planned)

```bash
# 0. Back up the phone (persist, modem, boot, dtbo, vbmeta)
# 1. Build kernel on GitHub macOS runners (blacktop/darwin-xnu-build)
gh workflow run xnu.yml -R YOU/ios-lemon
gh run download RUN_ID -R YOU/ios-lemon -n xnu-kernel -D xnu/out

# 2. Build iOS root image (on Linux)
tools/mkiosroot.sh OS.dmg SystemOS.dmg AppOS.dmg ios16-root.img 16G
tools/lemon-root-tweaks.py /mnt/iosroot
img2simg ios16-root.img ios16-root.simg

# 3. Build boot image
tools/mkadt.py shim/out/lemon.adt --highmem
tools/mkpayload.py xnu/out/kernel.development.lemon shim/out/lemon.adt shim/out/payload.bin \
    --cmdline '...'
shim/build.sh ../shim/out/payload.bin

# 4. Flash
fastboot -S 512M flash userdata ios16-root.simg
fastboot boot shim/out/shim-boot.img
```

## Credits

Built on Apple's open-source releases (xnu, IOHIDFamily, libpthread, hfs), [BearSSL](https://bearssl.org), [blacktop/darwin-xnu-build](https://github.com/blacktop/darwin-xnu-build), [ipsw](https://github.com/blacktop/ipsw), Qualcomm/Xiaomi's published Linux kernel sources, and the [ios-sweet](https://github.com/dipa-studio/ios-sweet) architecture. iOS itself is Apple's and is not distributed here.