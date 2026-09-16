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

> **If you are flashing the commit that added the Win layer, do a settings reset first.**
> The layer count went from 10 to 11, and ZMK Studio pins the layer list in the settings
> partition, which flashing does *not* erase. Skip the reset and the symptom is that every
> layer works except Win. See "Only layers 0–3 work" below for the full procedure — the
> order matters, and getting it wrong leaves the keyboard unusable until you redo it.

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
| 1 | Kp | `Kp` toggle | stock keypad; Space / Backspace / Enter all match base, keypad zero on the left big inner |
| 2 | Fn | `Fn` | stock F-keys |
| 3 | Mod | `Mod` | Bluetooth, backlight, bootloader, Studio unlock, Colemak toggle |
| 4 | Nav | hold left thumb `Del` | arrows, word/line motion, window + desktop management |
| 5 | Sym | hold `PgUp` (right thumb) | symbols, code operators |
| 6 | Num | hold `Home` (left thumb) | numpad on the right hand |
| 7 | IDE | hold `PgDn` (right thumb) | IntelliJ |
| 8 | Colemak | `Mod` + `Caps` | Colemak-DH practice |
| 9 | Mouse | hold **or tap** the right thumb's outer top key | pointer, clicks, scrolling |
| 10 | Win | hold **or tap** the blank key left of `H` | Rectangle Pro — snapping, displays, Spaces, layouts |

### Thumb clusters

| | Left | Right |
|---|---|---|
| top pair | `Ctrl` `Alt` | `Cmd` `Mouse` |
| small, nearest centre gap | `Home` = Num (hold) | `PgUp` = Sym (hold) |
| small, below those | `End` = Num (sticky) | `PgDn` = IDE (hold) |
| big keys | `Space`, `Del` / Nav (hold) | `Enter`, `Backspace` |

Left thumbs reach right-hand layers and vice versa, so nothing becomes a same-finger chord.

### The four blank keys

Each half has an extra innermost column, the one Kinesis puts `Kp` and `Mod` on. The two
keys below those are blank from the factory:

| Position | Where | Bound to |
|---|---|---|
| 20 | right of `T` | bootloader, on the `Mod` layer |
| 21 | left of `Y` | bootloader, on the `Mod` layer |
| 34 | right of `G` | still free |
| 39 | left of `H` | **Win layer** — hold, or tap to lock on |

Position 39 is the Win key. Right index holds it, left hand does the work, so window
management follows the same cross-hand rule as everything else.

---

## Home-row mods

Tap for the letter, hold for the modifier.

```
A     S     D     F              J      K     L     ;
Opt   Ctrl  Cmd   Shift          Shift  Cmd   Ctrl  Opt
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
H  ←           J  ↓            K  ↑           L  →       ;  line start   '  line end
N  line start  M  word left    ,  word right  .  line end
↑  PgUp        ↓  PgDn
```

Left hand, window and desktop management:

```
4  screenshot region → clipboard
Q  prev desktop   W  Mission Control   E  next desktop   R  app windows   T  Spotlight
A  app switcher   S  next window       D  fullscreen     F  show desktop  G  minimize
Z  undo           X  cut               C  copy           V  paste
```

`Nav`+`4` sends `Ctrl+Shift+Cmd+4` — drag to select a region, image goes to the clipboard.
It lives here because the home-row mods cannot produce it: `Ctrl`/`Shift`/`Cmd` are all
left-hand (`S`/`F`/`D`) and so is `4`, which `hold-trigger-key-positions` blocks by design.
Drop the `LC()` from the `SHOT` define in `config/adv360.keymap` to save a file to the
desktop instead.

Both `Shift` keys stay transparent, so Shift+arrow selection works while navigating.

**Two pairs for line start/end, because no single pair works everywhere:**

| Keys | Sends | Works in |
|---|---|---|
| `;` `'` | `Ctrl+A` / `Ctrl+E` | terminals, zsh/readline, native macOS text fields, VS Code |
| `N` `.` | `Cmd+←` / `Cmd+→` | IntelliJ, browsers, most macOS apps |

These were `Home` / `End` until they proved useless on macOS: in native Cocoa text views
(Notes, Mail, Safari fields, most Electron apps) `Home` scrolls the *viewport* to the top of
the document and leaves the caret where it was. `Ctrl+A` / `Ctrl+E` are true caret motions.

IntelliJ's default macOS keymap does *not* bind `Ctrl+A` / `Ctrl+E` — that's the
"macOS System Shortcuts" keymap variant. Use `N` / `.` in the IDE, or bind them under
Settings → Keymap → "Move Caret to Line Start".

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

### Mouse — hold the right thumb's outer top key, or tap to lock it on

```
left hand                 right hand
    E   = up                U  scroll up
S   D   F = left/down/right H  scroll left    ;  scroll right
                            J  left click     K  right click    L  middle click
                            M  scroll down
```

**Hold** for a quick point-and-click — release and you are back to typing.
**Tap** to lock the layer on for dragging or long scrolls, and tap again to leave.
`Esc` also drops you straight back to Base, so there are two ways out.

Left hand drives the cursor, right hand clicks and scrolls. Vertical scroll sits
directly above and below the left-click key; horizontal scroll flanks the clicks
either side.

**Tuning.** Three numbers, all near the top of `config/adv360.keymap` except the last:

| Setting | Now | Effect |
|---|---|---|
| `MOUSE_SPD` | 3600 | Top cursor speed, in pixels per second. Crosses a 3440px ultrawide in about a second. |
| `SCRL_SPD` | 12 | Scroll step size. |
| `time-to-max-speed-ms` (in the `&mmv` override at the end of the file) | 300 | How long to reach top speed. Lower feels twitchier, higher gives finer control at the start. |

The cursor deliberately starts slow and accelerates, so short taps land precisely
and a held key crosses the screen.

`MOUSE_SPD` is not DPI — it is a speed, not a sensitivity, because there is no
physical movement to scale. A 2550 DPI mouse only hits 2550 px/s when you actually
drag it an inch per second, and in practice you flick it far faster than that, so
match the feel rather than the number. The ceiling is 32767; past roughly 5000 the
cursor gets hard to stop on a target.

### Win — hold the blank key left of `H`, or tap to lock it on

Drives [Rectangle Pro](https://rectangleapp.com/pro). The left hand is a 3×3 grid laid out
like the screen — top row snaps to the top, bottom row to the bottom — with the two outer
columns throwing the window somewhere else entirely.

```
Q  top left     W  top half     E  top right    R  prev display   T  next display
A  left half    S  maximize     D  right half   F  prev Space     G  next Space
Z  bottom left  X  bottom half  C  bottom right V  split layout   B  tile 2×2
`  restore     Caps centre      ←  smaller      →  larger
```

`Esc` drops you straight back to Base, exactly as on the Mouse layer.

**Side by side vs stacked.** `A` / `D` split a display vertically, `W` / `X` split it
horizontally. Both are first-class because the LG runs in portrait, where stacking is the
useful split, while the Dell ultrawide wants side by side.

**Repeating a half cycles its size.** `A` `A` `A` gives left ½ → left ⅔ → left ⅓, in place.
That is Rectangle's `subsequentExecutionMode`, deliberately set to *resize* rather than
*cycle displays* — `R` and `T` already do displays, and they do it without resizing.

**`V` cycles a two-window layout:** side by side, then stacked, then ⅔ + ⅓.

**`F` / `G` take the window with you.** The Nav layer's `Q` / `E` move *you* between Spaces
and leave the window behind; Win's `F` / `G` move the window too. Rectangle implements this
by grabbing the title bar and firing the system Space shortcut, so
System Settings → Keyboard → Keyboard Shortcuts → Mission Control → "Move left/right a
space" has to stay enabled on its `Ctrl`+arrow defaults.

#### Why Hyper

Every key on this layer sends **`Ctrl`+`Opt`+`Cmd`+`Shift`** plus a letter, written in the
keymap as `HYP(k)`. Nothing in macOS or any application binds four modifiers, so the entire
family is free and no shortcut on this layer can ever be shadowed by the app in front. You
never type these by hand — the keyboard is the only thing that produces them.

The letter always matches the physical key, so the Win layer, the table below and
`bin/rectangle-pro-setup.sh` line up one to one.

Both `Shift` keys stay transparent, which reserves a second tier for later: holding Shift on
this layer produces a five-modifier chord that Rectangle can bind separately — `⇧R` for
*Previous Display Ratio*, say, which preserves relative size across displays of very
different shapes.

#### The Rectangle Pro side

```bash
./bin/rectangle-pro-setup.sh          # apply
./bin/rectangle-pro-setup.sh --show   # print what is currently bound
./bin/rectangle-pro-setup.sh --reset  # unbind
```

It writes `com.knollsoft.Hookshot` defaults directly, so the binding is reproducible on a new
machine and reviewable in git rather than clicked into a settings pane. Rectangle Pro's
General tab still has a "Restore Default Shortcuts & Snap Areas" button if you want out.

One thing it cannot do: **the `V` layout**. Layouts are stored in an encoded blob, so build
that one in Settings → Layouts by hand. The script prints the recipe when it finishes.

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
`bin/keymap-diagram.py` counts them and refuses to run if a layer is wrong, so it is worth
running as a cheap pre-flight check before pushing:

```bash
python3 bin/keymap-diagram.py     # validates, and regenerates docs/keymap.html
```

Re-run it after **any** keymap change — `docs/keymap.html` is generated, never hand-edited.

The stock `hm` behavior is left byte-identical to upstream (including its deprecated
`quick_tap_ms` spelling) to keep the diff minimal; the new `hml` / `hmr` behaviors use the
current `quick-tap-ms`.

`HYP(k)` expands to `LC(LA(LG(LS(k))))`. Four-deep modifier nesting is ordinary preprocessor
work — the same mechanism as the `LS(LG(LBKT))` bindings on the Nav layer, one level deeper.

`&none` blocks fall-through, so a key that should reach a layer from a *toggled* layer has to
be `&trans` there explicitly. That is why position 39 is `&trans` on both `keypad` and
`colemak`: without it, toggling either one would strand the Win layer out of reach.

All properties used here were verified present in the pinned ZMK fork
(`refil/zmk` @ `adv360-z3.5-2`) rather than assumed.

---

## Verify after flashing

| Test | Expect |
|---|---|
| Type `asdf jkl` at speed | plain letters, no modifiers |
| Hold `D`, press `C` | Cmd+C |
| Hold right thumb outer top, press `F` | cursor moves right |
| Tap right thumb outer top, press `J` | left click — tap again to leave the layer |
| Hold `D`, press `S` | plain `ds` — bilateral combos blocking a same-hand mod |
| Hold `F` for a second | `fffff` |
| Tap `J`+`K` together | `Esc` |
| Hold left thumb `Del`, press `H J K L` | ← ↓ ↑ → |
| Tap left thumb `Del` alone | forward delete |
| Hold `PgUp`, press `A` `S` | `(` `)` |
| `Mod` + `Caps`, then type `asdf` | `arst` |
| Tap `Caps`, type `hello world` | `HELLO world` |
| Hold the blank key left of `H`, press `A` then `D` | window snaps to the left half, then the right |
| Same, press `A` three times | left ½ → ⅔ → ⅓, without moving display |
| Same, press `T` twice | window walks Retina → LG → Dell |
| Same, press `G` | window moves to the next Space, and you follow it |
| Same, press `W` on the portrait LG | top half |
| Tap that key, press `A`, then `Esc` | layer locks on, snaps, then returns to Base |

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
