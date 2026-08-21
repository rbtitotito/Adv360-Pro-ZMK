#!/usr/bin/env python3
"""Render config/adv360.keymap as an HTML cheat sheet, one diagram per layer.

Parses the keymap rather than duplicating it, so the diagrams cannot drift out of
sync with the firmware. Re-run after any keymap change:

    python3 bin/keymap-diagram.py

Writes docs/keymap.html
"""

import re
import os
import sys

SRC = "config/adv360.keymap"
OUT = "docs/keymap.html"

# ---------------------------------------------------------------- geometry
KW, KH = 54, 38
COL_L = [20 + 58 * i for i in range(7)]
COL_R = [480 + 58 * i for i in range(7)]
ROW = [20 + 46 * r for r in range(5)]

POS = {}
for i in range(7):                       # row 0
    POS[i] = (COL_L[i], ROW[0])
    POS[7 + i] = (COL_R[i], ROW[0])
for i in range(7):                       # row 1
    POS[14 + i] = (COL_L[i], ROW[1])
    POS[21 + i] = (COL_R[i], ROW[1])
for i in range(7):                       # row 2
    POS[28 + i] = (COL_L[i], ROW[2])
    POS[39 + i] = (COL_R[i], ROW[2])
for i in range(6):                       # row 3
    POS[46 + i] = (COL_L[i], ROW[3])
    POS[54 + i] = (COL_R[i + 1], ROW[3])
for i in range(5):                       # row 4
    POS[60 + i] = (COL_L[i], ROW[4])
    POS[71 + i] = (COL_R[i + 2], ROW[4])

POS.update({                             # thumb clusters
    35: (194, 260), 36: (252, 260),
    65: (136, 306), 66: (194, 306), 52: (252, 306), 67: (252, 352),
    37: (596, 260), 38: (654, 260),
    53: (596, 306), 69: (654, 306), 70: (712, 306), 68: (596, 352),
})
assert len(POS) == 76, len(POS)

SVG_W, SVG_H = 900, 410

# ---------------------------------------------------------------- keycodes
KC = {
    "EQUAL": "=", "MINUS": "-", "BSLH": "\\", "SQT": "'", "SEMI": ";",
    "COMMA": ",", "DOT": ".", "FSLH": "/", "LBKT": "[", "RBKT": "]",
    "GRAVE": "`", "UNDER": "_", "PLUS": "+", "COLON": ":", "DQT": '"',
    "EXCL": "!", "AT": "@", "HASH": "#", "DLLR": "$", "PRCNT": "%",
    "CARET": "^", "AMPS": "&amp;", "ASTRK": "*", "LPAR": "(", "RPAR": ")",
    "LBRC": "{", "RBRC": "}", "PIPE": "|", "TILDE": "~",
    "LT": "&lt;", "GT": "&gt;",
    "BSPC": "Bksp", "DEL": "Del", "RET": "Enter", "ENTER": "Enter",
    "SPACE": "Space", "TAB": "Tab", "ESC": "Esc", "CAPS": "Caps",
    "LSHFT": "Shift", "RSHFT": "Shift", "LCTRL": "Ctrl", "RCTRL": "Ctrl",
    "LALT": "Opt", "RALT": "Opt", "LGUI": "Cmd", "RGUI": "Cmd",
    "HOME": "Home", "END": "End", "PG_UP": "PgUp", "PG_DN": "PgDn",
    "LEFT": "←", "RIGHT": "→", "UP": "↑", "DOWN": "↓",
    "KP_NUM": "Num", "KP_EQUAL": "K=", "KP_DIVIDE": "K/",
    "KP_MULTIPLY": "K*", "KP_MINUS": "K-", "KP_PLUS": "K+",
    "KP_ENTER": "KEnt", "KP_DOT": "K.",
}
for n in range(10):
    KC[f"N{n}"] = str(n)
    KC[f"KP_N{n}"] = f"K{n}"
for n in range(1, 13):
    KC[f"F{n}"] = f"F{n}"

MODSYM = {"LG": "⌘", "RG": "⌘", "LA": "⌥", "RA": "⌥",
          "LC": "⌃", "RC": "⌃", "LS": "⇧", "RS": "⇧"}

MOD_SHORT = {"LGUI": "Cmd", "RGUI": "Cmd", "LALT": "Opt", "RALT": "Opt",
             "LCTRL": "Ctrl", "RCTRL": "Ctrl", "LSHFT": "Shift", "RSHFT": "Shift"}


def kc(tok):
    """Render a keycode, unwrapping nested modifier functions like LS(LG(A))."""
    m = re.fullmatch(r"([LR][GACS])\((.*)\)", tok)
    if m:
        return MODSYM[m.group(1)] + kc(m.group(2))
    return KC.get(tok, tok)


MACRO_LABEL = {
    "arrow": "->", "fatarrow": "=>", "noteq": "!=", "eqeqeq": "===",
    "dcolon": "::", "srch_evr": "Srch Evr", "gitst": "git status",
    "gitcm": 'git ci -m"', "macro_ver": "version",
}


def label(binding, layer_names):
    """-> (main, sub, kind).  kind drives colouring."""
    parts = binding.split()
    b, args = parts[0], parts[1:]

    if b == "kp":
        return kc(args[0]), "", "key"
    if b == "trans":
        return "▽", "", "trans"
    if b == "none":
        return "", "", "none"
    if b == "caps_word":
        return "CapsWd", "", "special"
    if b == "mo":
        return layer_names[int(args[0])], "hold", "nav"
    if b == "tog":
        return layer_names[int(args[0])], "toggle", "nav"
    if b == "to":
        return layer_names[int(args[0])], "go to", "nav"
    if b == "sl":
        return layer_names[int(args[0])], "sticky", "nav"
    if b == "lt":
        return kc(args[1]), "hold " + layer_names[int(args[0])], "nav"
    if b in ("hml", "hmr", "hm"):
        return kc(args[1]), "hold " + MOD_SHORT.get(args[0], args[0]), "hrm"
    if b == "sk":
        return kc(args[0]), "sticky", "special"
    if b == "bt":
        return ("BT clr" if args[0] == "BT_CLR" else "BT " + args[-1]), "", "special"
    if b == "bl":
        return {"BL_TOG": "Light", "BL_INC": "Light +",
                "BL_DEC": "Light -"}.get(args[0], args[0]), "", "special"
    if b == "rgb_ug":
        return "LEDs", "", "special"
    if b == "stp":
        return "Battery", "", "special"
    if b == "bootloader":
        return "Boot", "", "special"
    if b == "studio_unlock":
        return "Unlock", "", "special"
    if b in MACRO_LABEL:
        return MACRO_LABEL[b], "", "macro"
    return b, "", "special"


# ---------------------------------------------------------------- descriptions
LAYER_NOTES = {
    "Base": "QWERTY with home-row mods. Tap a home-row key for its letter, hold it "
            "for a modifier. Modifiers only engage when the next key is on the "
            "<em>other</em> hand, so same-hand rolls never misfire.",
    "Kp": "Stock Kinesis keypad, toggled on and off with the Kp key. Space, "
          "Backspace and Enter sit on the same thumb keys as the base layer, so "
          "they do not move when you toggle it.",
    "Fn": "Stock function row. F1–F12 replace the number row.",
    "Mod": "Radio, lighting and firmware controls. Also where the Colemak toggle "
           "and the ZMK Studio unlock live.",
    "Red": "Navigation. Right hand drives the cursor, left hand drives macOS "
           "windows and desktops. Both Shift keys stay transparent so "
           "Shift+arrow selection still works.",
    "Purple": "Symbols on the left hand, code operators on the right. Underscore "
              "and plus come free by holding Shift over minus and equals.",
    "Cyan": "Numpad on the right hand. Hold Home for a run of digits, or tap End "
            "for a single one.",
    "Yellow": "IntelliJ, using the macOS keymap. Left hand for navigation and "
              "refactoring, right hand for the debugger.",
    "Colemak": "Colemak-DH practice. Only the letters change — punctuation, "
               "numbers, thumbs and every other layer stay put, so the rest of "
               "your muscle memory carries over.",
}

DESC = {
    # --- macOS windows & desktops (Nav, left hand)
    "kp LC(LEFT)": "Previous desktop / Space",
    "kp LC(RIGHT)": "Next desktop / Space",
    "kp LC(UP)": "Mission Control — show all windows",
    "kp LC(DOWN)": "App Exposé — windows of the current app",
    "kp LG(SPACE)": "Spotlight search",
    "kp LG(TAB)": "Application switcher",
    "kp LG(GRAVE)": "Next window of the same app",
    "kp LC(LG(F))": "Toggle fullscreen",
    "kp F11": "Show desktop",
    "kp LG(M)": "Minimise window",
    "kp LG(Z)": "Undo",
    "kp LG(X)": "Cut",
    "kp LG(C)": "Copy",
    "kp LG(V)": "Paste",
    # --- history & tabs (Nav, right hand)
    "kp LG(LBKT)": "Back (browser / IntelliJ navigate back)",
    "kp LG(RBKT)": "Forward",
    "kp LS(LG(LBKT))": "Previous tab",
    "kp LS(LG(RBKT))": "Next tab",
    # --- cursor motion
    "kp LG(LEFT)": "Jump to start of line",
    "kp LG(RIGHT)": "Jump to end of line",
    "kp LA(LEFT)": "Move one word left",
    "kp LA(RIGHT)": "Move one word right",
    "kp LEFT": "Cursor left", "kp RIGHT": "Cursor right",
    "kp UP": "Cursor up", "kp DOWN": "Cursor down",
    "kp HOME": "Start of line", "kp END": "End of line",
    "kp PG_UP": "Page up", "kp PG_DN": "Page down",
    # --- IntelliJ (Yellow, left hand)
    "kp LS(LG(A))": "Find Action — search every command",
    "kp LG(E)": "Recent Files",
    "kp LS(LG(F))": "Find in Files",
    "kp LS(LG(O))": "Go to File",
    "kp LC(R)": "Run",
    "kp LC(D)": "Debug",
    "kp LG(B)": "Go to Declaration",
    "kp LA(LG(B))": "Go to Implementation",
    "kp LA(LG(L))": "Reformat Code",
    "kp LA(RET)": "Show Intention Actions — the quick-fix menu",
    "kp LS(LG(RET))": "Complete Statement",
    "kp LS(F6)": "Rename symbol",
    "kp LA(LG(T))": "Surround With",
    "kp LA(LG(V))": "Extract Variable",
    "kp LA(LG(M))": "Extract Method",
    # --- IntelliJ debugger (Yellow, right hand)
    "kp F7": "Step into",
    "kp F8": "Step over",
    "kp LS(F8)": "Step out",
    "kp LA(LG(R))": "Resume program",
    "kp LG(F8)": "Toggle breakpoint",
    # --- macros
    "arrow": "Types <code>-&gt;</code>",
    "fatarrow": "Types <code>=&gt;</code>",
    "noteq": "Types <code>!=</code>",
    "eqeqeq": "Types <code>===</code>",
    "dcolon": "Types <code>::</code>",
    "srch_evr": "Search Everywhere — double-taps Shift",
    "gitst": "Types <code>git status</code>",
    "gitcm": "Types <code>git commit -m \"</code>, cursor inside the quotes",
    "macro_ver": "Types the firmware build stamp (date, branch, commit)",
    # --- system
    "studio_unlock": "Unlocks the keyboard for Clique / ZMK Studio",
    "bootloader": "Reboots this half into the bootloader for flashing",
    "bt BT_CLR": "Clears the Bluetooth pairing on this profile",
    "stp STP_BAT": "Reports battery level",
    "rgb_ug RGB_TOG": "Toggles the indicator LEDs",
    "bl BL_TOG": "Toggles the backlight",
    "bl BL_INC": "Backlight brighter",
    "bl BL_DEC": "Backlight dimmer",
    "kp CAPS": "Caps Lock",
}
for _n in range(5):
    DESC[f"bt BT_SEL {_n}"] = f"Switch to Bluetooth profile {_n}"


def describe(binding, layer_names):
    """Plain-English explanation, or None if the key speaks for itself."""
    p = binding.split(); b = p[0]
    if b == "mo":
        return f"Hold for the <b>{layer_names[int(p[1])]}</b> layer"
    if b == "tog":
        return f"Toggle the <b>{layer_names[int(p[1])]}</b> layer on and off"
    if b == "to":
        return f"Switch to the <b>{layer_names[int(p[1])]}</b> layer"
    if b == "sl":
        return f"Sticky <b>{layer_names[int(p[1])]}</b> — applies to the next key only"
    if b == "lt":
        return (f"Tap for <b>{kc(p[2])}</b>, hold for the "
                f"<b>{layer_names[int(p[1])]}</b> layer")
    if b in ("hml", "hmr", "hm"):
        return (f"Tap for <b>{kc(p[2])}</b>, hold for "
                f"<b>{MOD_SHORT.get(p[1], p[1])}</b>")
    if b == "caps_word":
        return "Types the next word in capitals, releases on space"
    return DESC.get(binding)


# ---------------------------------------------------------------- parsing
LAYER_BEHAVIORS = ("mo", "tog", "to", "sl", "lt")


def resolve(tok, defs):
    """The keymap refers to layers by #define name; swap those for indices."""
    p = tok.split()
    if p[0] in LAYER_BEHAVIORS and len(p) > 1 and p[1] in defs:
        p[1] = str(defs[p[1]])
        return " ".join(p)
    return tok


def parse(path):
    src = open(path).read()
    defs = {m[0]: int(m[1])
            for m in re.findall(r"^#define\s+(\w+)\s+(\d+)\s*$", src, re.M)}
    km = src[src.index("keymap {"):]
    layers = []
    for name, disp, body in re.findall(
        r"(\w+)\s*\{\s*display-name = \"([^\"]+)\";\s*bindings = <(.*?)>;", km, re.S
    ):
        toks = [re.sub(r"\s+", " ", p).strip() for p in body.split("&") if p.strip()]
        if len(toks) != 76:
            sys.exit(f"ERROR: layer '{name}' has {len(toks)} bindings, expected 76")
        layers.append({"name": name, "disp": disp,
                       "bindings": [resolve(t, defs) for t in toks]})
    if not layers:
        sys.exit("ERROR: no layers parsed")
    return layers


# ---------------------------------------------------------------- rendering
FILL = {
    "key": ("#ffffff", "#d7d5cc", "#2c2c2a"),
    "trans": ("#faf9f5", "#e6e4dc", "#b4b2a9"),
    "none": ("#f4f3ee", "#e6e4dc", "#b4b2a9"),
    "nav": ("#EEEDFE", "#7F77DD", "#26215C"),
    "hrm": ("#E1F5EE", "#5DCAA5", "#04342C"),
    "macro": ("#FAEEDA", "#EF9F27", "#412402"),
    "special": ("#E6F1FB", "#85B7EB", "#042C53"),
}


def esc(s):
    return s if "&amp;" in s or "&lt;" in s or "&gt;" in s else (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def svg(layer, layer_names):
    out = [f'<svg viewBox="0 0 {SVG_W} {SVG_H}" class="kb">']
    for i, binding in enumerate(layer["bindings"]):
        main, sub, kind = label(binding, layer_names)
        x, y = POS[i]
        bg, br, fg = FILL[kind]
        out.append(
            f'<rect x="{x}" y="{y}" width="{KW}" height="{KH}" rx="5" '
            f'fill="{bg}" stroke="{br}" stroke-width="1"/>'
        )
        if main:
            fs = 13 if len(main) <= 5 else (11 if len(main) <= 8 else 9)
            ty = y + (18 if sub else 24)
            out.append(
                f'<text x="{x + KW/2}" y="{ty}" text-anchor="middle" '
                f'font-size="{fs}" fill="{fg}">{esc(main)}</text>'
            )
        if sub:
            out.append(
                f'<text x="{x + KW/2}" y="{y + 31}" text-anchor="middle" '
                f'font-size="8.5" fill="{fg}" opacity="0.75">{esc(sub)}</text>'
            )
    out.append("</svg>")
    return "\n".join(out)


# Physical keycap legends, so navigation can be described by the key you look at
# rather than a matrix index.
PHYS = {
    0: "=", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "Kp",
    7: "Mod", 8: "6", 9: "7", 10: "8", 11: "9", 12: "0", 13: "-",
    14: "Tab", 15: "Q", 16: "W", 17: "E", 18: "R", 19: "T", 20: "macro key",
    21: "macro key", 22: "Y", 23: "U", 24: "I", 25: "O", 26: "P", 27: "\\",
    28: "Esc", 29: "A", 30: "S", 31: "D", 32: "F", 33: "G", 34: "macro key",
    35: "Ctrl (L thumb)", 36: "Alt (L thumb)",
    37: "Cmd (R thumb)", 38: "Ctrl (R thumb)",
    39: "macro key", 40: "H", 41: "J", 42: "K", 43: "L", 44: ";", 45: "'",
    46: "Shift (L)", 47: "Z", 48: "X", 49: "C", 50: "V", 51: "B",
    52: "Home (L thumb, upper small)", 53: "PgUp (R thumb, upper small)",
    54: "N", 55: "M", 56: ",", 57: ".", 58: "/", 59: "Shift (R)",
    60: "Fn (left)", 61: "`", 62: "Caps", 63: "←", 64: "→",
    65: "Bksp (L thumb, big outer)", 66: "Del (L thumb, big inner)",
    67: "End (L thumb, lower small)", 68: "PgDn (R thumb, lower small)",
    69: "Enter (R thumb)", 70: "Space (R thumb)",
    71: "↑", 72: "↓", 73: "[", 74: "]", 75: "Fn (right)",
}


def nav_summary(layers):
    """Which keys reach which layer, derived from the bindings."""
    names = [l["disp"] for l in layers]
    reach = {n: [] for n in names}
    for li, layer in enumerate(layers):
        for pos, b in enumerate(layer["bindings"]):
            p = b.split()
            if p[0] in ("mo", "tog", "to", "sl") and len(p) > 1 and p[1].isdigit():
                tgt = int(p[1])
            elif p[0] == "lt" and len(p) > 2 and p[1].isdigit():
                tgt = int(p[1])
            else:
                continue
            if tgt >= len(names):
                continue
            verb = {"mo": "hold", "tog": "toggle", "to": "go to",
                    "sl": "sticky tap", "lt": "hold"}[p[0]]
            reach[names[tgt]].append((names[li], pos, verb))
    return reach


CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
 margin:0;padding:32px;background:#faf9f5;color:#2c2c2a;line-height:1.6}
h1{font-size:24px;font-weight:500;margin:0 0 4px}
h2{font-size:19px;font-weight:500;margin:36px 0 2px}
h3{font-size:15px;font-weight:500;margin:16px 0 2px;color:#5f5e5a}
.sub{color:#5f5e5a;font-size:14px;margin:0 0 10px}
.kb{width:100%;max-width:900px;display:block;margin-bottom:8px}
.card{background:#fff;border:1px solid #e6e4dc;border-radius:12px;
 padding:16px 20px;margin-bottom:20px}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;margin:12px 0 24px}
.legend span{display:flex;align-items:center;gap:6px}
.sw{width:14px;height:14px;border-radius:3px;border:1px solid}
table{border-collapse:collapse;font-size:14px;margin:8px 0 0}
th,td{text-align:left;padding:5px 14px 5px 0;border-bottom:1px solid #e6e4dc}
th{font-weight:500;color:#5f5e5a}
.on{color:#5f5e5a}
code{background:#f1efe8;padding:1px 5px;border-radius:4px;font-size:13px}
@media print{body{padding:0;background:#fff}.card{break-inside:avoid;
 page-break-inside:avoid}h2{page-break-after:avoid}}
"""


def main():
    if not os.path.exists(SRC):
        sys.exit(f"ERROR: run from the repo root ({SRC} not found)")
    layers = parse(SRC)
    names = [l["disp"] for l in layers]
    reach = nav_summary(layers)

    h = ["<!DOCTYPE html><html><head><meta charset='utf-8'>",
         "<title>Advantage360 Pro keymap</title>",
         f"<style>{CSS}</style></head><body>",
         "<h1>Advantage360 Pro keymap</h1>",
         "<p class='sub'>Generated from <code>config/adv360.keymap</code> by "
         "<code>bin/keymap-diagram.py</code>. Do not edit by hand.</p>",
         "<div class='legend'>"]
    for kind, lbl in [("key", "key"), ("hrm", "home-row mod"),
                      ("nav", "layer navigation"), ("macro", "macro"),
                      ("special", "system"), ("trans", "▽ falls through")]:
        bg, br, _ = FILL[kind]
        h.append(f"<span><i class='sw' style='background:{bg};"
                 f"border-color:{br}'></i>{lbl}</span>")
    h.append("</div>")

    h.append("<h2>Reaching each layer</h2><table>"
             "<tr><th>Layer</th><th>How to get there</th></tr>")
    for n in names:
        srcs = reach.get(n, [])
        if not srcs:
            txt = "<em>base layer — always active</em>" if n == names[0] else "—"
        else:
            txt = ", ".join(
                f"{v} <b>{PHYS.get(p, p)}</b>"
                + ("" if l == names[0] else f" <span class='on'>on {l}</span>")
                for l, p, v in srcs)
        h.append(f"<tr><td><b>{n}</b></td><td>{txt}</td></tr>")
    h.append("</table>")

    for i, layer in enumerate(layers):
        h.append(f"<h2>{i} &middot; {layer['disp']}</h2>")
        srcs = reach.get(layer["disp"], [])
        if layer["disp"] in LAYER_NOTES:
            h.append(f"<p class='sub'>{LAYER_NOTES[layer['disp']]}</p>")
        if srcs:
            h.append("<p class='sub'>Reach it: " + ", ".join(
                f"{v} <b>{PHYS.get(p, p)}</b>"
                + ("" if l == names[0] else f" on {l}")
                for l, p, v in srcs) + "</p>")
        elif i == 0:
            h.append("<p class='sub'>Always active. All other layers stack on top.</p>")
        h.append("<div class='card'>" + svg(layer, names))
        rows = []
        seen = set()
        for pos, binding in enumerate(layer["bindings"]):
            d = describe(binding, names)
            if not d or binding in seen:
                continue
            seen.add(binding)
            rows.append(f"<tr><td><b>{PHYS.get(pos, pos)}</b></td><td>{d}</td></tr>")
        if rows:
            h.append("<h3>What these keys do</h3><table>" + "".join(rows) + "</table>")
        h.append("</div>")

    h.append("</body></html>")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write("\n".join(h))
    print(f"wrote {OUT}  ({len(layers)} layers)")


if __name__ == "__main__":
    main()
