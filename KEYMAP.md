# Rob's Advantage360 Pro keymap (macOS)

Personal keymap layered on top of the Kinesis V3.0 config. Everything lives in
`config/adv360.keymap` — that single file is the source of truth.

---

## Build and flash

Push to this fork; GitHub Actions builds automatically (~5 min). Open the run, download the
artifact zip — it contains `left.uf2` and `right.uf2`.

The two "macro" keys are the **blank key immediately right of `T`** (left half) and
**immediately left of `Y`** (right half).

1. Connect the **left** module via USB.
2. `Mod` + blank-key-right-of-`T` → mounts as a USB drive.
3. Copy `left.uf2` to it. The drive disconnects on its own.
4. Unplug both halves, switch both off.
5. Switch the **left** half on.
6. Connect the **right** module via USB.
7. `Mod` + blank-key-left-of-`Y`. Copy `right.uf2` to the drive.
8. Unplug the right half, switch it back on.

Physical reset buttons are the fallback — User Manual §2.7 for location, §5.9 for use.
`settings-reset.uf2` in the repo root recovers a bad flash.

### Staying current with upstream

```bash
git fetch upstream
git rebase upstream/V3.0
```

Conflicts should be confined to `config/adv360.keymap`, since that's the only tracked file
this branch modifies.

### Clique still works

`&studio_unlock` is kept on the Mod layer, so Clique connects as before (`Mod`+`Esc` to
unlock) and is fine for one-off experiments. But Clique writes to the keyboard's saved
settings, and those are overwritten on the next flash — so anything you want to keep belongs
in this file.

---

## Layers

| # | Name | Held by | Contents |
|---|---|---|---|
| 0 | Base | — | QWERTY + home-row mods |
| 1 | Kp | `Kp` toggle | stock keypad, thumbs matched to base (Space / Backspace, no Delete) |
| 2 | Fn | `Fn` | stock F-keys |
| 3 | Mod | `Mod` | Bluetooth, backlight, bootloader, Studio unlock, Colemak toggle |
| 4 | Red — Nav | hold left thumb `Del` | arrows, word/line motion, window + desktop management |
| 5 | Purple — Sym | hold `PgUp` (right thumb) | symbols, code operators |
| 6 | Cyan — Num | hold `Home` (left thumb) | numpad on the right hand |
| 7 | Yellow — IDE | hold `PgDn` (right thumb) | IntelliJ |
| 8 | Colemak | `Mod` + `Caps` | Colemak-DH practice |

### Thumb clusters

| | Left | Right |
|---|---|---|
| top pair | `Ctrl` `Alt` | `Cmd` `Ctrl` |
| small, nearest centre gap | `Home` = Num (hold) | `PgUp` = Sym (hold) |
| small, below those | `End` = Num (sticky) | `PgDn` = IDE (hold) |
| big keys | `Space`, `Del` / Nav (hold) | `Enter`, `Backspace` |

Left thumbs reach right-hand layers and vice versa, so nothing becomes a same-finger chord.

---

## Home-row mods

Tap for the letter, hold for the modifier.

```
A     S     D     F              J      K     L     ;
Cmd   Opt   Ctrl  Shift          Shift  Ctrl  Opt   Cmd
```

Three guards keep them from misfiring during normal typing:

- **`require-prior-idle-ms = 150`** — a hold is ignored if you were typing within the last
  150 ms. This kills most false positives on its own.
- **`hold-trigger-key-positions`** — bilateral combos. A left-hand mod only engages if the
  next key is on the right hand or a thumb, so same-hand rolls like `sd` or `df` can never
  produce a modifier.
- **`quick-tap-ms = 175`** — tap-then-hold repeats the letter instead of engaging the mod, so
  holding `F` to repeat `fff` still works.

Thumb modifiers remain as a fallback.

### Tuning

Edit `tapping-term-ms` in the `hml` / `hmr` behaviors:

| Symptom | Fix |
|---|---|
| Mods fire when you meant to type | raise `tapping-term-ms` to 280–300, or `require-prior-idle-ms` to 200 |
| You hold but get a letter | lower `tapping-term-ms` to 200–220 |
| Can't get a mod on the same hand as its target | working as designed — use the thumb modifier |

---

## Layer contents

### Nav — hold left thumb `Del`

Right hand, motion:

```
Y  back        U  prev tab     I  next tab    O  forward
H  ←           J  ↓            K  ↑           L  →       ;  Home   '  End
N  line start  M  word left    ,  word right  .  line end
↑  PgUp        ↓  PgDn
```

Left hand, window and desktop management:

```
Q  prev desktop   W  Mission Control   E  next desktop   R  app windows   T  Spotlight
A  app switcher   S  next window       D  fullscreen     F  show desktop  G  minimize
Z  undo           X  cut               C  copy           V  paste
```

Both `Shift` keys stay transparent, so Shift+arrow selection works while navigating.

### Sym — hold `PgUp`

```
Tab =    Q ^    W &    E *    R +    T \
Esc -    A (    S )    D {    F }    G |
         Z [    X ]    C <    V >    B ~
```

Right hand carries code operators: `Y` → `->`, `U` → `=>`, `I` → `!=`, `O` → `===`, `P` → `::`

`_` and `+` come free by holding Shift over `-` and `=`.

### Num — hold `Home`, or tap `End` for a single digit

```
U 7   I 8   O 9   P -
H 0   J 4   K 5   L 6   ; +   ' *
N ,   M 1   , 2   . 3   / .
```

`End` is `&sl` (sticky layer, 1 s window): tap it, type one digit,
it releases itself. This is not a true num-word — ZMK has no built-in equivalent to Caps Word
for digits. A real auto-exiting version needs urob's `zmk-num-word` module.

### IDE — hold `PgDn`

```
Tab Search Everywhere   Q Find Action     W Recent Files    E Find in Files
R   Go to File          T Run
A   Go to Declaration   S Reformat        D Debug           F Intention Actions
G   Complete Statement
Z   Rename              X Surround With   C Extract Var     V Extract Method
B   Go to Implementation
```

Right hand, debugging: `H` step into, `J` step over, `K` step out, `L` resume,
`;` toggle breakpoint. Plus `Y` types `git status`, `U` types `git commit -m "`.

Search Everywhere is IntelliJ's double-tap-Shift, emitted as a macro. Double-tap detection is
timing-sensitive — if it doesn't register, raise `tap-ms` on `srch_evr` above 40.

### Colemak-DH — `Mod` + `Caps` toggles

```
Q W F P B      J L U Y ;
A R S T G      M N E I O
Z X C D V      K H , . /
```

Home-row mods carry over in the same physical positions. Everything else — numbers,
punctuation, thumbs, all other layers — is transparent, so only the alphas change.

The 360's wells are already column-staggered, so the "angle mod" that Colemak-DH needs on
flat boards doesn't apply here.

### Combos

Both keys within 40 ms, guarded by the same 150 ms idle requirement:

- `J` + `K` → `Esc`
- `D` + `F` → `Tab`
- `K` + `L` → `Enter`

`Caps Word` is on the `Caps` key: tap, type a word in caps, releases on space.

---

## Notes on the config

Key positions come from `assets/key-positions.md`. The `KEYS_L` / `KEYS_R` / `THUMBS` defines
at the top of the keymap cover positions 0–75 exactly, with no gaps or duplicates, and are
what `hold-trigger-key-positions` uses to implement bilateral combos.

Every layer must contain exactly 76 bindings, in rows of 14 / 14 / 18 / 14 / 16. A miscount
is the most common build failure and the error message doesn't always point at the right line.

The stock `hm` behavior is left byte-identical to upstream (including its deprecated
`quick_tap_ms` spelling) to keep the diff minimal; the new `hml` / `hmr` behaviors use the
current `quick-tap-ms`.

All properties used here were verified present in the pinned ZMK fork
(`refil/zmk` @ `adv360-z3.5-2`) rather than assumed.

---

## Verify after flashing

| Test | Expect |
|---|---|
| Type `asdf jkl` at speed | plain letters, no modifiers |
| Hold `A`, press `C` | Cmd+C |
| Hold `A`, press `S` | plain `as` — bilateral combos blocking a same-hand mod |
| Hold `F` for a second | `fffff` |
| Tap `J`+`K` together | `Esc` |
| Hold left thumb `Del`, press `H J K L` | ← ↓ ↑ → |
| Tap left thumb `Del` alone | forward delete |
| Hold `PgUp`, press `A` `S` | `(` `)` |
| `Mod` + `Caps`, then type `asdf` | `arst` |
| Tap `Caps`, type `hello world` | `HELLO world` |

---

## Troubleshooting

### Only layers 0–3 work, and Clique lists four layers

Seen after first flashing the firmware that introduced layers 4–8. The firmware was fine —
the Actions build log confirmed the keymap reached the devicetree and every layer compiled.

**Cause:** ZMK Studio persists keymap state to the settings partition, and flashing firmware
does **not** erase that partition. Stale state from before those layers existed pinned the
layer list at four. Per-key values from the newly compiled keymap still showed through, which
made the new firmware look live and sent us chasing the wrong thing for hours.

**Fix:** settings reset on both halves, then reflash firmware on both halves.

### Settings reset — read this before starting

Getting the order wrong leaves the keyboard unusable until it's done correctly.

- **After a settings reset the keymap is gone, so `Mod` + macro key cannot enter the
  bootloader.** Use the physical bootloader button: paperclip, quick **double-click**.
- **One module connected at a time**, the other unplugged and switched off.
- **Reset, then firmware, on each half.** `settings-reset.uf2` is itself a firmware image and
  leaves that half disabled until a real image follows it.
- **Power the left half on first**, then the right. The left is the split central; the right
  only searches for a peer that's already advertising.

### Reading the symptoms

| Symptom | Meaning |
|---|---|
| Right half flashing red | Can't find the central. Expected until the left half has firmware. |
| Left half types nothing | Left is still running the reset utility, not firmware. |
| `Mod` + `V` types a build stamp | e.g. `20260816-rob-eec6fac-clique`. Confirms which commit is running, and `-clique` vs `-.` tells you which artifact. |

### On macOS the flash "error" is success

```
cp: fcopyfile failed: Input/output error
cp: fchmod failed: Device not configured
```

That is what a **successful** UF2 flash looks like. The bootloader reboots the instant it has
the full image, so the device vanishes mid-copy. Use `cp` rather than Finder — Finder writes
resource-fork files that can confuse the bootloader.

### Which artifact to flash

`firmware-clique`, not `firmware-no-clique` — `&studio_unlock` is inert without it. The two
jobs also produce **different** `right.uf2` binaries (the version macro differs), so always
flash both halves from the same artifact zip.
