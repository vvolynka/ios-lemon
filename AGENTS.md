# Working on ios-lemon

- Read `NOTES.md` before starting; it contains the project goal, hardware facts,
  current blocker, local artifact locations and the next concrete action.
- The user switches agents frequently. Update the active handoff in `NOTES.md`
  after each milestone and before stopping. Record commits, CI run IDs, exact
  build/boot results and unfinished work. Distinguish observations from guesses.
- Commit completed changes. Use `gh` for GitHub Actions kernel builds and logs.
  Local single-file cross-compiles are useful before spending a CI run.
- Device bring-up uses temporary `fastboot boot` images. Preserve the Android
  installation and partition backups. The user approved using internal UFS for
  iOS and said Android may be deleted: the iOS root goes into the existing
  `userdata` partition (no GPT changes). Keep bootloaders, recovery, modem,
  persist and the backups intact, and confirm each destructive step with the
  user before running it.
- Keep device dumps, serial numbers and downloaded Apple artifacts out of git.

## Lemon (SM6115) specific notes

- SoC: SM6115 (Snapdragon 662) - different from sweet's SM7150
- CPU: 4× Cortex-A73 + 4× Cortex-A53 (8 cores total, big.LITTLE)
- GICv3 with different base addresses
- Timer: 19.2 MHz (same as sweet)
- PSCI via SMC (same as sweet)
- Need to extract stock DTB from lemon's boot.img to get MMIO layout
- Display: 1080×2400 @60Hz (different refresh rate from sweet's 120Hz)
- Touch: Likely Goodix or Focaltech on different I2C/SPI bus
- PMIC: PM6150 (same family as sweet, different config)
- Storage: UFS 2.1 or eMMC 5.1 (verify from DTB)