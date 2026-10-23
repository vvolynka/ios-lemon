# iOS 16 on lemon (Redmi 9T NFC, SM6115) - working notes

## Agent handoff / active work (2026-10-22, initial)

### Project created: 2026-10-22

**GOAL:** Port iOS 16 (XNU xnu-8796) to Redmi 9T NFC (lemon, SM6115/Snapdragon 662), following the ios-sweet architecture.

**STATE:** Fresh project created. No kernel built, no boot tested.

### Hardware facts (from public datasheets / Linux kernel sources - need verification from live DTB)

| Item | sweet (SM7150) | lemon (SM6115) | Notes |
|------|----------------|----------------|-------|
| CPU | 2×A76 + 6×A55 | 4×A73 + 4×A53 | Different core types, same 8 cores |
| GICD | 0x17a00000 | ? | Need live DTB |
| GICR | 0x17a60000 | ? | Need live DTB |
| Framebuffer | 0x9c000000 | ? | ABL leaves splash at different addr |
| UFS | 0x01d84000 | ? | Different controller |
| RPMh | ? | ? | Different regulator layout |
| Timer | 19.2 MHz | 19.2 MHz | Same |
| PSCI | SMC | SMC | Same |
| VTIMER_INTID | 19 (PPI 3) | ? | Qualcomm-specific |
| Display | 1080×2400 @120Hz | 1080×2400 @60Hz | Different panel/timing |
| Touch | Goodix GT9896 @GENI SE7 | ? | Different bus/address |
| Buttons | PMIC PON + PM6150L GPIO2 | ? | Different PMIC config |

### IMMEDIATE NEXT STEPS

1. **Extract stock DTB from lemon's boot.img** - need user's phone backup
   ```bash
   python3 tools/unpack_bootv2.py backup/boot.img dtb/boot_unpacked
   ```
   This gives the live FDT with all MMIO addresses, interrupt mappings, memory layout.

2. **Create lemon-specific mkadt.py** - adapt from sweet's mkadt.py using live DTB data

3. **Create lemon shim** - adapt shim.c with lemon's addresses (GIC, timer, framebuffer, UFS, RPMh)

4. **Create initial XNU patches** - start with toolchain compat, machine config, non-PAC, stubs (patches 0001-0009 from sweet)

5. **Build kernel on GitHub Actions** - use blacktop/darwin-xnu-build workflow

6. **Test on QEMU first** - tools/qemu-lemon.py with virt machine

### Key differences from sweet to address

- **CPU topology**: 4×A73 + 4×A53 vs 2×A76 + 6×A55 - different cluster config
- **GIC base addresses**: Almost certainly different on SM6115
- **Framebuffer address**: ABL puts splash at different physical address
- **UFS controller**: Different base address / compatible string
- **RPMh regulator layout**: Different rails for touch, display, etc.
- **Touch controller**: Different I2C bus, possibly different chip (Goodix vs Focaltech)
- **Display panel**: 60Hz vs 120Hz, different timings
- **Memory layout**: Different reserved regions, possibly different RAM size

### Files to create (in priority order)

1. `tools/unpack_bootv2.py` - copy from sweet (works for any Android boot.img v2)
2. `tools/mkadt.py` - lemon version with correct addresses from live DTB
3. `shim/` - all C/asm files with lemon addresses
4. `tools/mkpayload.py` - adapt for lemon (mostly same, just different ADT)
5. `tools/qemu-lemon.py` - QEMU test with virt machine
6. `xnu/patches/0001-*.patch` - first patch: toolchain compatibility

### Live DTB needed

User needs to provide (from phone in fastboot/EDL):
- `backup/boot.img` - stock boot image
- `backup/dtbo.img` - if separate
- `backup/persist.img`, `backup/modemst1/2`, etc. - for calibration data

### Build environment

- Linux PC with `aarch64-linux-gnu-gcc`, `mkbootimg`, `fastboot`, `adb`
- GitHub account for macOS CI runners (free for public repos)
- iPhone X (iPhone10,3) iOS 16.7.16 (20H392) IPSW from Apple

---

### Session log

**2026-10-22** - Project created by user request. Created directory structure, README.md, AGENTS.md, this NOTES.md. Waiting for user to provide stock boot.img for DTB extraction.

**2026-10-23** - Ported the full ios-sweet (SM7150) codebase into ios-lemon as the starting scaffold: copied and renamed `shim/`, `tools/`, `xnu/patches/` (80+ patches), `.github/workflows/xnu.yml`, `docs/`, `.gitignore` (sweet -> lemon identifiers). Lemon-specific hardware addresses remain placeholders pending the live DTB from stock boot.img (GIC, framebuffer, UFS, RPMh). Next: extract stock DTB, update mkadt.py/shim addresses, build kernel via GitHub Actions.