#!/usr/bin/env bash
#
# Bind Rectangle Pro to the Win layer of config/adv360.keymap.
#
# The keyboard sends Hyper (Ctrl+Opt+Cmd+Shift) plus a letter; this script tells
# Rectangle Pro what each of those chords means. The letter always matches the
# physical key on the Win layer, so the keymap and this file line up one to one.
#
# Nothing on macOS binds four modifiers, so none of these can collide with a
# system or application shortcut.
#
#   ./bin/rectangle-pro-setup.sh          apply
#   ./bin/rectangle-pro-setup.sh --show   print what is currently bound
#   ./bin/rectangle-pro-setup.sh --reset  unbind everything this script sets
#
# Reversible either way: Rectangle Pro's General tab also has a
# "Restore Default Shortcuts & Snap Areas" button.

set -euo pipefail

BUNDLE="com.knollsoft.Hookshot"
APP="/Applications/Rectangle Pro.app"

# Ctrl 262144 + Opt 524288 + Cmd 1048576 + Shift 131072
HYPER=1966080

# Rectangle Pro action  |  macOS virtual keycode  |  the key you press on the Win layer
#
# The keycodes are the standard Carbon virtual keycodes. They are what Rectangle
# stores, and they are positional, so they are correct for QWERTY. If you are in
# the Colemak layer the Win layer still sends the QWERTY letter, so these hold.
BINDINGS=(
  # --- 3x3 grid: the left hand laid out like the screen -------------------
  "topLeft          12  Q"
  "topHalf          13  W"
  "topRight         14  E"
  "leftHalf          0  A"
  "maximize          1  S"
  "rightHalf         2  D"
  "bottomLeft        6  Z"
  "bottomHalf        7  X"
  "bottomRight       8  C"
  # --- throw the window somewhere else ------------------------------------
  "previousDisplay  15  R"
  "nextDisplay      17  T"
  "prevSpace         3  F"
  "nextSpace         5  G"
  # --- multiple windows ----------------------------------------------------
  "tile2x2          11  B"
  # --- adjustments ---------------------------------------------------------
  "restore          16  \`"
  "center           32  Caps"
  "smaller          34  <-"
  "larger           31  ->"
)

# Hyper+V (keycode 9) is deliberately absent: it drives the "Split" Layout,
# and Layouts are stored in an encoded blob that cannot be written with
# `defaults`. See the reminder printed at the end of this script.

die() { printf '%s\n' "$*" >&2; exit 1; }

[ -d "$APP" ] || die "Rectangle Pro is not installed at $APP"

case "${1:-}" in
  --show)
    printf '%-18s %s\n' "ACTION" "CURRENT BINDING"
    for row in "${BINDINGS[@]}"; do
      read -r action _ _ <<<"$row"
      cur=$(defaults read "$BUNDLE" "$action" 2>/dev/null | tr -d '\n ' || true)
      printf '%-18s %s\n' "$action" "${cur:-<unset>}"
    done
    exit 0
    ;;
  --reset)
    for row in "${BINDINGS[@]}"; do
      read -r action _ _ <<<"$row"
      defaults delete "$BUNDLE" "$action" 2>/dev/null || true
    done
    echo "Unbound $(( ${#BINDINGS[@]} )) shortcuts. Restart Rectangle Pro to pick this up."
    exit 0
    ;;
  "") ;;
  *) die "unknown argument: $1" ;;
esac

# ---------------------------------------------------------------- shortcuts
for row in "${BINDINGS[@]}"; do
  read -r action keycode key <<<"$row"
  defaults write "$BUNDLE" "$action" \
    -dict keyCode -float "$keycode" modifierFlags -float "$HYPER"
  printf '  Hyper+%-5s -> %s\n' "$key" "$action"
done

# ---------------------------------------------------------------- behaviour
# Repeated commands: "cycle sizes on half actions". SubsequentExecutionMode.resize
# is 0 in Rectangle's source. This is what makes pressing Hyper+A three times give
# left half -> left two thirds -> left third, rather than hopping between displays
# (the Win layer has dedicated keys, Hyper+R and Hyper+T, for that).
defaults write "$BUNDLE" subsequentExecutionMode -int 0

# Which sizes that cycle walks through. Bit 0 = 2/3, bit 1 = 1/2, bit 2 = 1/3,
# so 7 gives 1/2 -> 2/3 -> 1/3. cycleSizesIsChanged makes it read this value
# instead of falling back to the built-in default set.
defaults write "$BUNDLE" selectedCycleSizes -int 7
defaults write "$BUNDLE" cycleSizesIsChanged -bool true

# Hyper is not a combination macOS reserves, but this keeps the shortcut
# recorder from second-guessing anything added by hand later.
defaults write "$BUNDLE" allowAnyShortcut -bool true

# Follow the window when it is thrown to another display.
defaults write "$BUNDLE" moveCursorAcrossDisplays -int 2

# ---------------------------------------------------------------- restart
if pgrep -xq "Rectangle Pro"; then
  osascript -e 'quit app "Rectangle Pro"' >/dev/null 2>&1 || true
  # Rectangle Pro writes its own defaults on quit, so let it finish before relaunching.
  for _ in $(seq 20); do pgrep -xq "Rectangle Pro" || break; sleep 0.2; done
fi
open -g "$APP"

cat <<'EOF'

Done. Two things this script cannot do for you:

1. The Split layout (Hyper+V)
   Layouts live in an encoded blob, so build this one in the GUI:
   Settings -> Layouts -> "+ Layout" -> empty layout, named "Split",
   shortcut Ctrl+Opt+Cmd+Shift+V.

     entry   app       press 1      press 2       press 3
     1       Global    Left Half    Top Half      First Two Thirds
     2       Global    Right Half   Bottom Half   Last Third

   Use the + on each entry to add presses 2 and 3. Turn on "Bring windows to
   front"; leave "All windows, beyond first match" off.

2. macOS Spaces shortcuts
   Rectangle Pro's Next/Previous Space works by grabbing the window's title bar
   and then firing the system shortcut for switching Spaces. So
   System Settings -> Keyboard -> Keyboard Shortcuts -> Mission Control ->
   "Move left a space" / "Move right a space" must be enabled, on their
   defaults of Ctrl+Left and Ctrl+Right.

EOF
