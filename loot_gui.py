"""
Offline D&D 5e loot generator with Tkinter GUI.
Uses SRD-style random treasure tables for individual opponents or hoards.
Tables are embedded to keep the app portable.
"""
from __future__ import annotations

import json
import math
import os
import random
import tkinter as tk
import urllib.request
from dataclasses import dataclass
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

# ------------------------- dice utilities -------------------------


def roll_dice(num: int, die: int, multiplier: int = 1) -> int:
    return sum(random.randint(1, die) for _ in range(num)) * multiplier


def parse_dice(expr: str) -> Tuple[int, int, int]:
    """Return (num, die, multiplier) for strings like "4d6*10" or "2d4"."""
    if "d" not in expr:
        raise ValueError(f"Invalid dice expression: {expr}")
    parts = expr.split("d")
    num = int(parts[0])
    if "*" in parts[1]:
        die_str, mult_str = parts[1].split("*")
        return num, int(die_str), int(mult_str)
    return num, int(parts[1]), 1


def roll_expr(expr: str) -> int:
    num, die, mult = parse_dice(expr)
    return roll_dice(num, die, mult)


# ------------------------- treasure tables -------------------------

@dataclass
class CoinEntry:
    cp: str = "0"
    sp: str = "0"
    ep: str = "0"
    gp: str = "0"
    pp: str = "0"


def coin_from_entry(entry: CoinEntry) -> Dict[str, int]:
    coins: Dict[str, int] = {}
    for denom, expr in [
        ("cp", entry.cp),
        ("sp", entry.sp),
        ("ep", entry.ep),
        ("gp", entry.gp),
        ("pp", entry.pp),
    ]:
        if expr and expr != "0":
            coins[denom] = roll_expr(expr)
    return coins


# Individual treasure (DMG/SRD random treasure tables)
INDIVIDUAL_TABLES: List[Tuple[Tuple[float, float], List[Tuple[int, int, CoinEntry]]]] = [
    # challenge 0-4
    ((0, 4), [
        (30, CoinEntry(cp="5d6")),
        (60, CoinEntry(sp="4d6")),
        (70, CoinEntry(ep="3d6")),
        (95, CoinEntry(gp="3d6")),
        (100, CoinEntry(pp="1d6")),
    ]),
    # challenge 5-10
    ((5, 10), [
        (30, CoinEntry(cp="4d6*100")),
        (60, CoinEntry(sp="6d6*10")),
        (70, CoinEntry(ep="3d6*10")),
        (95, CoinEntry(gp="4d6*10")),
        (100, CoinEntry(pp="2d6*10")),
    ]),
    # challenge 11-16
    ((11, 16), [
        (20, CoinEntry(sp="4d6*100")),
        (35, CoinEntry(ep="1d6*100")),
        (75, CoinEntry(gp="2d6*100")),
        (100, CoinEntry(pp="2d6*10")),
    ]),
    # challenge 17+
    ((17, math.inf), [
        (15, CoinEntry(gp="2d6*100")),
        (55, CoinEntry(gp="2d6*100", pp="1d6*10")),
        (100, CoinEntry(gp="2d6*100", pp="2d6*10")),
    ]),
]

# Gems and art packages referenced by hoards
GEM_PACKAGES: Dict[str, Tuple[str, str]] = {
    "10 gp": ("2d6", "10 gp gems"),
    "50 gp": ("2d6", "50 gp gems"),
    "100 gp": ("2d4", "100 gp gems"),
    "500 gp": ("3d6", "500 gp gems"),
    "1000 gp": ("3d6", "1,000 gp precious gems"),
}

ART_PACKAGES: Dict[str, Tuple[str, str]] = {
    "25 gp": ("2d4", "25 gp art objects"),
    "250 gp": ("2d4", "250 gp art objects"),
    "750 gp": ("2d4", "750 gp art objects"),
}

# Condensed magic item tables (SRD items only).
def _load_magic_tables() -> Dict[str, List[Tuple[int, int, str]]]:
    """Load dungeonmastertools magic tables if available; otherwise use the condensed SRD set."""
    import json

    try:
        raw = json.loads(open("magic_tables.json", "r", encoding="utf-8").read())
        return {k: [(int(threshold), item) for threshold, item in v] for k, v in raw.items()}
    except Exception:
        return {
            "A": [
                (50, "Potion of healing"),
                (60, "Spell scroll (cantrip)"),
                (70, "Potion of climbing"),
                (90, "Spell scroll (1st level)"),
                (94, "Spell scroll (2nd level)"),
                (98, "Potion of greater healing"),
                (99, "Bag of holding"),
                (100, "Driftglobe"),
            ],
            "B": [
                (15, "Potion of greater healing"),
                (22, "Potion of fire breath"),
                (29, "Potion of resistance"),
                (34, "+1 ammunition"),
                (39, "Potion of animal friendship"),
                (44, "Potion of hill giant strength"),
                (49, "Potion of growth"),
                (54, "Potion of water breathing"),
                (59, "Spell scroll (2nd level)"),
                (64, "Spell scroll (3rd level)"),
                (67, "Bag of holding"),
                (69, "Keoghtom's ointment"),
                (71, "Oil of slipperiness"),
                (73, "Dust of disappearance"),
                (75, "Dust of dryness"),
                (77, "Dust of sneezing and choking"),
                (79, "Elemental gem"),
                (81, "Philter of love"),
                (84, "Alchemy jug"),
                (87, "Cap of water breathing"),
                (90, "Cloak of the manta ray"),
                (92, "Driftglobe"),
                (94, "Goggles of night"),
                (96, "Tankard of sobriety"),
                (98, "Rope of climbing"),
                (100, "Wand of magic detection"),
            ],
            "C": [
                (15, "Potion of superior healing"),
                (22, "+1 weapon"),
                (27, "Spell scroll (4th level)"),
                (32, "+1 ammunition"),
                (36, "Potion of clairvoyance"),
                (40, "Potion of diminution"),
                (44, "Potion of gaseous form"),
                (48, "Potion of frost giant strength"),
                (52, "Potion of stone giant strength"),
                (56, "Potion of heroism"),
                (60, "Potion of invulnerability"),
                (64, "Potion of mind reading"),
                (67, "Spell scroll (5th level)"),
                (70, "Elixir of health"),
                (73, "Oil of etherealness"),
                (76, "Potion of fire giant strength"),
                (79, "Quaal's feather token"),
                (82, "Scroll of protection"),
                (84, "Bag of holding"),
                (86, "Portable hole"),
                (88, "Boots of elvenkind"),
                (90, "Cloak of elvenkind"),
                (92, "Eyes of minute seeing"),
                (94, "Gloves of swimming and climbing"),
                (96, "Hat of disguise"),
                (98, "Potion of poison"),
                (100, "Ring of swimming"),
            ],
            "F": [
                (15, "+1 weapon"),
                (25, "Potion of supreme healing"),
                (35, "Spell scroll (6th level)"),
                (45, "Spell scroll (7th level)"),
                (55, "Spell scroll (8th level)"),
                (65, "+2 weapon"),
                (70, "Potion of storm giant strength"),
                (75, "Potion of invulnerability"),
                (80, "Spellguard shield"),
                (85, "+1 amulet of the devout"),
                (90, "Ring of evasion"),
                (95, "Ring of protection"),
                (100, "Rod of absorption"),
            ],
            "G": [
                (11, "Weapon, +2"),
                (22, "Figurine of wondrous power"),
                (33, "Potion of speed"),
                (44, "Spell scroll (8th level)"),
                (55, "Spell scroll (7th level)"),
                (66, "+3 weapon"),
                (77, "Amulet of health"),
                (88, "Boots of speed"),
                (94, "Diamond necklace"),
                (100, "Ring of regeneration"),
            ],
            "H": [
                (10, "+2 armor"),
                (20, "+3 weapon"),
                (30, "Cloak of invisibility"),
                (40, "Ring of spell turning"),
                (50, "Rod of lordly might"),
                (60, "Vorpal sword"),
                (70, "Manual of quickness of action"),
                (80, "Staff of power"),
                (90, "Ring of three wishes"),
                (100, "Apparatus of Kwalish"),
            ],
        }


MAGIC_TABLES: Dict[str, List[Tuple[int, int, str]]] = _load_magic_tables()

# Lightweight spell cache so spell scrolls can show real spell names
SPELL_CACHE_FILE = "spells_cache.json"
SPELLS_BY_LEVEL: Dict[int, List[str]] = {}
# Fallback minimal spell lists per level to avoid empty scroll picks
DEFAULT_SPELLS = {
    0: ["Mage Hand", "Light", "Minor Illusion"],
    1: ["Magic Missile", "Cure Wounds", "Shield"],
    2: ["Invisibility", "Lesser Restoration"],
    3: ["Fireball", "Counterspell"],
    4: ["Polymorph", "Greater Invisibility"],
    5: ["Cone of Cold", "Raise Dead"],
    6: ["Chain Lightning", "Heal"],
    7: ["Teleport", "Finger of Death"],
    8: ["Mind Blank", "Power Word Stun"],
    9: ["Wish", "Meteor Swarm"],
}


def _fetch_spells_from_open5e() -> Dict[int, List[str]]:
    spells: Dict[int, List[str]] = {i: [] for i in range(0, 10)}
    try:
        url = "https://api.open5e.com/v1/spells/"
        next_url = url
        while next_url:
            with urllib.request.urlopen(next_url) as resp:  # type: ignore[arg-type]
                data = json.loads(resp.read().decode("utf-8"))
            for spell in data.get("results", []):
                lvl = spell.get("level_int")
                name = spell.get("name")
                if isinstance(lvl, int) and isinstance(name, str):
                    spells.setdefault(lvl, []).append(name)
            next_url = data.get("next")
        return spells
    except Exception:
        return spells


def _load_spells_cache() -> Dict[int, List[str]]:
    if os.path.exists(SPELL_CACHE_FILE):
        try:
            with open(SPELL_CACHE_FILE, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            parsed: Dict[int, List[str]] = {}
            for k, v in raw.items():
                try:
                    key = int(k)
                except Exception:
                    continue
                if isinstance(v, list):
                    parsed[key] = [str(x) for x in v]
            return parsed
        except Exception:
            return {}
    return {}


def _ensure_spells() -> None:
    # Purely local spell list; no network requests.
    # This keeps spell scroll expansion deterministic and offline-friendly.
    global SPELLS_BY_LEVEL
    if SPELLS_BY_LEVEL:
        return
    SPELLS_BY_LEVEL = dict(DEFAULT_SPELLS)


def _expand_spell_scroll(item: str) -> str:
    if not item.lower().startswith("spell scroll"):
        return item
    level_text = item.lower()
    level_map = {
        "cantrip": 0,
        "1st": 1,
        "2nd": 2,
        "3rd": 3,
        "4th": 4,
        "5th": 5,
        "6th": 6,
        "7th": 7,
        "8th": 8,
        "9th": 9,
    }
    target_level = None
    for key, val in level_map.items():
        if key in level_text:
            target_level = val
            break
    if target_level is None:
        return item
    _ensure_spells()
    spells = SPELLS_BY_LEVEL.get(target_level) or DEFAULT_SPELLS.get(target_level, [])
    if not spells:
        return item
    spell_name = random.choice(spells)
    return f"Spell scroll (level {target_level if target_level>0 else 'cantrip'}): {spell_name}"

# Hoard entries are intentionally simplified but keep the structure of the SRD tables.
HOARD_TABLES = {
    "0-4": {
        "coins": CoinEntry(cp="6d6*100", sp="3d6*100", gp="2d6*10"),
        "rows": [
            (6, {}),
            (16, {"gems": "10 gp"}),
            (26, {"art": "25 gp"}),
            (36, {"gems": "50 gp"}),
            (52, {"gems": "10 gp", "magic": [("A", "1d6")]}),
            (60, {"art": "25 gp", "magic": [("A", "1d6")]}),
            (70, {"gems": "50 gp", "magic": [("A", "1d6")]}),
            (80, {"gems": "50 gp", "magic": [("B", "1d4")]}),
            (90, {"art": "25 gp", "magic": [("B", "1d4")]}),
            (100, {"gems": "50 gp", "magic": [("C", "1d4")]})
        ],
    },
    "5-10": {
        "coins": CoinEntry(cp="2d6*100", sp="2d6*1000", gp="6d6*100", pp="3d6*10"),
        "rows": [
            (4, {}),
            (10, {"gems": "50 gp"}),
            (16, {"art": "25 gp"}),
            (22, {"gems": "100 gp"}),
            (28, {"art": "250 gp"}),
            (36, {"gems": "100 gp", "magic": [("A", "1d6")]}),
            (44, {"art": "250 gp", "magic": [("A", "1d6")]}),
            (52, {"gems": "100 gp", "magic": [("B", "1d4")]}),
            (60, {"art": "250 gp", "magic": [("B", "1d4")]}),
            (70, {"gems": "100 gp", "magic": [("C", "1d4")]}),
            (85, {"art": "250 gp", "magic": [("F", "1d2")]}),
            (100, {"gems": "100 gp", "magic": [("G", "1d1")]})
        ],
    },
    "11-16": {
        "coins": CoinEntry(sp="4d6*1000", gp="1d6*1000", pp="1d6*100"),
        "rows": [
            (2, {}),
            (6, {"gems": "100 gp"}),
            (10, {"art": "250 gp"}),
            (12, {"gems": "500 gp"}),
            (14, {"art": "750 gp"}),
            (22, {"gems": "500 gp", "magic": [("C", "1d4"), ("F", "1d1")]}),
            (30, {"art": "750 gp", "magic": [("C", "1d4"), ("F", "1d1")]}),
            (38, {"gems": "500 gp", "magic": [("F", "1d2")]}) ,
            (46, {"art": "750 gp", "magic": [("F", "1d2")]}) ,
            (60, {"gems": "500 gp", "magic": [("G", "1d1")]}) ,
            (75, {"art": "750 gp", "magic": [("G", "1d1")]}) ,
            (100, {"gems": "1000 gp", "magic": [("H", "1d1")]}) ,
        ],
    },
    "17+": {
        "coins": CoinEntry(gp="4d6*1000", pp="5d6*100"),
        "rows": [
            (2, {}),
            (5, {"art": "250 gp"}),
            (8, {"gems": "500 gp"}),
            (10, {"art": "750 gp"}),
            (12, {"gems": "1000 gp"}),
            (20, {"gems": "1000 gp", "magic": [("F", "1d2"), ("G", "1d1")]}),
            (35, {"art": "750 gp", "magic": [("F", "1d2"), ("G", "1d1")]}),
            (50, {"gems": "1000 gp", "magic": [("G", "1d2")]}),
            (65, {"art": "750 gp", "magic": [("G", "1d2")]}),
            (80, {"gems": "1000 gp", "magic": [("H", "1d1")]}),
            (100, {"art": "750 gp", "magic": [("H", "1d1")]}),
        ],
    },
}


def pick_table_for_cr(cr: float) -> Tuple[Tuple[float, float], List[Tuple[int, int, CoinEntry]]]:
    for rng, entries in INDIVIDUAL_TABLES:
        low, high = rng
        if low <= cr <= high:
            return rng, entries
    return INDIVIDUAL_TABLES[-1]


def roll_table(entries: List[Tuple[int, int, CoinEntry]]) -> Dict[str, int]:
    roll = random.randint(1, 100)
    for threshold, coins in entries:
        if roll <= threshold:
            return coin_from_entry(coins)
    return {}


def _extend_table_with_custom(base: List[Tuple[int, int, str]], custom: List[str]) -> List[Tuple[int, int, str]]:
    if not custom:
        return base
    table = list(base)
    start = table[-1][0] if table else 0
    slots = len(custom)
    remaining = max(0, 100 - start)
    if remaining == 0:
        remaining = 100 // slots
        start = 0
    step = max(1, remaining // slots)
    current = start
    for idx, item in enumerate(custom):
        current = min(100, current + step)
        if idx == slots - 1:
            current = 100
        table.append((current, item))
    table.sort(key=lambda x: x[0])
    return table


def choose_magic(
    table: str,
    extra_by_table: Optional[Dict[str, List[str]]] = None,
    global_extra: Optional[List[str]] = None,
    cr_filtered: Optional[List[Tuple[Tuple[float, float], str]]] = None,
    cr: Optional[float] = None,
) -> str:
    extras = []
    if extra_by_table and table in extra_by_table:
        extras.extend(extra_by_table[table])
    if global_extra:
        extras.extend(global_extra)
    if cr is not None and cr_filtered:
        for (low, high), item in cr_filtered:
            if low <= cr <= high:
                extras.append(item)
    table_data = _extend_table_with_custom(MAGIC_TABLES.get(table, []), extras)
    if not table_data:
        return "(no items configured)"
    roll = random.randint(1, 100)
    for threshold, item in table_data:
        if roll <= threshold:
            return item
    return table_data[-1][1]


def roll_magic(
    table: str,
    dice: str,
    extra_by_table: Optional[Dict[str, List[str]]] = None,
    global_extra: Optional[List[str]] = None,
    cr_filtered: Optional[List[Tuple[Tuple[float, float], str]]] = None,
    cr: Optional[float] = None,
) -> List[str]:
    num = roll_expr(dice)
    results = [choose_magic(table, extra_by_table, global_extra, cr_filtered, cr) for _ in range(num)]
    return [_expand_spell_scroll(r) for r in results]


def roll_hoard(
    cr: float,
    extra_by_table: Optional[Dict[str, List[str]]] = None,
    global_extra: Optional[List[str]] = None,
    cr_filtered: Optional[List[Tuple[Tuple[float, float], str]]] = None,
) -> Dict[str, List[str]]:
    key = None
    if cr <= 4:
        key = "0-4"
    elif cr <= 10:
        key = "5-10"
    elif cr <= 16:
        key = "11-16"
    else:
        key = "17+"

    table = HOARD_TABLES[key]
    loot: Dict[str, List[str]] = {"coins": [], "gems": [], "art": [], "magic": []}
    coins = coin_from_entry(table["coins"])
    for coin, amt in coins.items():
        loot["coins"].append(f"{amt} {coin}")

    roll = random.randint(1, 100)
    for threshold, reward in table["rows"]:
        if roll <= threshold:
            if reward.get("gems"):
                dice, desc = GEM_PACKAGES[reward["gems"]]
                loot["gems"].append(f"{roll_expr(dice)} x {desc}")
            if reward.get("art"):
                dice, desc = ART_PACKAGES[reward["art"]]
                loot["art"].append(f"{roll_expr(dice)} x {desc}")
            for table_letter, dice in reward.get("magic", []):
                loot["magic"].extend(roll_magic(table_letter, dice, extra_by_table, global_extra, cr_filtered, cr))
            break
    return loot


INDIVIDUAL_MAGIC: List[Tuple[Tuple[float, float], Tuple[str, str]]] = [
    # (cr range), (magic table, dice expression)
    ((0, 4), ("A", "1d1")),
    ((5, 10), ("B", "1d1")),
    ((11, 16), ("C", "1d1")),
    ((17, math.inf), ("G", "1d2")),
]


def pick_individual_magic(cr: float) -> Tuple[str, str]:
    for rng, info in INDIVIDUAL_MAGIC:
        low, high = rng
        if low <= cr <= high:
            return info
    return INDIVIDUAL_MAGIC[-1][1]


def roll_individual(
    cr: float,
    include_magic: bool = True,
    extra_by_table: Optional[Dict[str, List[str]]] = None,
    global_extra: Optional[List[str]] = None,
    cr_filtered: Optional[List[Tuple[Tuple[float, float], str]]] = None,
) -> Dict[str, List[str]]:
    _, entries = pick_table_for_cr(cr)
    coins = roll_table(entries)
    loot: Dict[str, List[str]] = {"coins": [], "gems": [], "art": [], "magic": []}
    for coin, amt in coins.items():
        loot["coins"].append(f"{amt} {coin}")

    if include_magic:
        table, dice = pick_individual_magic(cr)
        loot["magic"].extend(roll_magic(table, dice, extra_by_table, global_extra, cr_filtered, cr))
    return loot


# ------------------------- GUI -------------------------

class EnemyRow:
    def __init__(self, parent: tk.Frame, row: int, on_remove):
        self.parent = parent
        self.row_frame = tk.Frame(parent)
        self.row_frame.grid(row=row, column=0, sticky="ew", pady=2)

        self.cr_var = tk.StringVar(value="1")
        self.count_var = tk.IntVar(value=1)
        self.hoard_var = tk.BooleanVar(value=False)

        ttk.Label(self.row_frame, text=f"Enemy {row+1} CR").grid(row=0, column=0, padx=2)
        ttk.Entry(self.row_frame, textvariable=self.cr_var, width=6).grid(row=0, column=1, padx=2)

        ttk.Label(self.row_frame, text="Count").grid(row=0, column=2, padx=2)
        ttk.Spinbox(self.row_frame, from_=1, to=20, textvariable=self.count_var, width=5).grid(row=0, column=3, padx=2)

        ttk.Checkbutton(self.row_frame, text="Hoard", variable=self.hoard_var).grid(row=0, column=4, padx=4)

        ttk.Button(self.row_frame, text="Remove", command=lambda: on_remove(self)).grid(row=0, column=5, padx=4)

    def destroy(self):
        self.row_frame.destroy()

    def values(self) -> Tuple[float, int, bool]:
        try:
            cr = float(self.cr_var.get())
        except ValueError:
            cr = 0
        count = max(1, self.count_var.get())
        return cr, count, self.hoard_var.get()


class LootApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("D&D 5e Loot Generator (SRD)")
        root.geometry("820x620")

        self.rows: List[EnemyRow] = []
        self.individual_magic_var = tk.BooleanVar(value=True)
        self.custom_file_var = tk.StringVar(value="custom_items.json")
        self.custom_status_var = tk.StringVar(value="")
        self.custom_tables: Dict[str, List[str]] = {}
        self.manual_items_by_table: Dict[str, List[str]] = {}
        self.manual_items_by_cr: List[Tuple[Tuple[float, float], str]] = []

        top = tk.Frame(root)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="Enter enemies (CR, count, hoard?) and generate loot:").pack(anchor="w")
        ttk.Checkbutton(top, text="Include magic items on individual treasure", variable=self.individual_magic_var).pack(anchor="w", pady=(2, 0))

        file_row = tk.Frame(root)
        file_row.pack(fill="x", padx=8, pady=(2, 2))
        ttk.Label(file_row, text="Custom items JSON (optional):").pack(side="left")
        ttk.Entry(file_row, textvariable=self.custom_file_var, width=35).pack(side="left", padx=(4, 4))
        ttk.Button(file_row, text="Load", command=self.load_custom_items_file).pack(side="left")
        ttk.Label(file_row, textvariable=self.custom_status_var, foreground="#555").pack(side="left", padx=6)

        manual_frame = tk.LabelFrame(root, text="Extra custom magic items (one per line, appended to all tables)")
        manual_frame.pack(fill="x", padx=8, pady=(2, 4))
        self.manual_text = tk.Text(manual_frame, height=4)
        self.manual_text.pack(fill="x", padx=4, pady=4)
        # Tooltip/help line to clarify format
        ttk.Label(
            manual_frame,
            text="Format: plain item names, e.g. 'Flame Tongue Sword' or 'Spell scroll (5th level)'. Each line is one item.",
            foreground="#555",
            wraplength=760,
            justify="left",
        ).pack(fill="x", padx=4, pady=(0, 4))

        save_row = tk.Frame(manual_frame)
        save_row.pack(fill="x", padx=4, pady=(0, 4))
        ttk.Button(save_row, text="Save custom items to JSON", command=self.save_custom_items_file).pack(side="left")
        self.save_status = tk.StringVar(value="")
        ttk.Label(save_row, textvariable=self.save_status, foreground="#555").pack(side="left", padx=6)

        scoped_frame = tk.LabelFrame(root, text="Add scoped custom item")
        scoped_frame.pack(fill="x", padx=8, pady=(0, 6))
        scoped_inner = tk.Frame(scoped_frame)
        scoped_inner.pack(fill="x", padx=4, pady=4)
        ttk.Label(scoped_inner, text="Item:").pack(side="left")
        self.scoped_item_var = tk.StringVar()
        ttk.Entry(scoped_inner, textvariable=self.scoped_item_var, width=30).pack(side="left", padx=(4, 8))

        ttk.Label(scoped_inner, text="Table:").pack(side="left")
        self.scoped_table_var = tk.StringVar(value="ALL")
        ttk.Combobox(scoped_inner, textvariable=self.scoped_table_var, values=["ALL", "A", "B", "C", "D", "E", "F", "G", "H", "I"], width=5, state="readonly").pack(side="left", padx=(2, 8))

        ttk.Label(scoped_inner, text="CR band:").pack(side="left")
        self.scoped_cr_var = tk.StringVar(value="Any")
        ttk.Combobox(scoped_inner, textvariable=self.scoped_cr_var, values=["Any", "0-4", "5-10", "11-16", "17+"], width=7, state="readonly").pack(side="left", padx=(2, 8))

        ttk.Button(scoped_inner, text="Add", command=self.add_scoped_item).pack(side="left")
        self.scoped_status = tk.StringVar(value="")
        ttk.Label(scoped_inner, textvariable=self.scoped_status, foreground="#555").pack(side="left", padx=6)

        # Attempt auto-load on startup
        self.load_custom_items_file(silent=True)

        self.rows_frame = tk.Frame(root)
        self.rows_frame.pack(fill="x", padx=8)
        self.add_row()

        controls = tk.Frame(root)
        controls.pack(fill="x", padx=8, pady=4)
        ttk.Button(controls, text="Add Enemy", command=self.add_row).pack(side="left", padx=4)
        ttk.Button(controls, text="Generate Loot", command=self.generate).pack(side="left", padx=4)
        ttk.Button(controls, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side="left", padx=4)

        self.output = tk.Text(root, wrap="word", height=25)
        self.output.pack(fill="both", expand=True, padx=8, pady=8)

    def add_row(self):
        row = EnemyRow(self.rows_frame, len(self.rows), self.remove_row)
        self.rows.append(row)

    def remove_row(self, row_obj: EnemyRow):
        if len(self.rows) == 1:
            return
        idx = self.rows.index(row_obj)
        row_obj.destroy()
        self.rows.pop(idx)
        for i, r in enumerate(self.rows):
            r.row_frame.grid(row=i, column=0, sticky="ew", pady=2)

    def generate(self):
        try:
            buffer: List[str] = []
            extra_by_table = dict(self.custom_tables)
            # Merge table-scoped manual items
            for tbl, items in self.manual_items_by_table.items():
                extra_by_table.setdefault(tbl, []).extend(items)
            global_extra = self._manual_items()
            cr_filtered = list(self.manual_items_by_cr)
            for idx, row in enumerate(self.rows, start=1):
                cr, count, hoard_flag = row.values()
                buffer.append(f"Enemy group {idx}: CR {cr}, count {count}, {'Hoard' if hoard_flag else 'Individual'}")
                for _ in range(count):
                    loot = (
                        roll_hoard(cr, extra_by_table, global_extra, cr_filtered)
                        if hoard_flag
                        else roll_individual(
                            cr,
                            include_magic=self.individual_magic_var.get(),
                            extra_by_table=extra_by_table,
                            global_extra=global_extra,
                            cr_filtered=cr_filtered,
                        )
                    )
                    buffer.extend(self._format_loot(loot))
                buffer.append("")
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "\n".join(buffer).strip())
        except Exception as exc:
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, f"Error while generating loot: {exc}")

    def _format_loot(self, loot: Dict[str, List[str]]) -> List[str]:
        lines: List[str] = []
        if loot["coins"]:
            lines.append("  Coins: " + ", ".join(loot["coins"]))
        if loot["gems"]:
            lines.append("  Gems: " + ", ".join(loot["gems"]))
        if loot["art"]:
            lines.append("  Art: " + ", ".join(loot["art"]))
        if loot["magic"]:
            lines.append("  Magic: " + ", ".join(loot["magic"]))
        if not lines:
            lines.append("  No additional treasure")
        return lines

    def copy_to_clipboard(self):
        text = self.output.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    # ------------------------- custom items helpers -------------------------

    def _manual_items(self) -> List[str]:
        raw = self.manual_text.get("1.0", tk.END).splitlines()
        return [line.strip() for line in raw if line.strip()]

    def _parse_cr_band(self, text: str) -> Tuple[float, float]:
        text = text.strip()
        if text == "0-4":
            return 0, 4
        if text == "5-10":
            return 5, 10
        if text == "11-16":
            return 11, 16
        if text == "17+":
            return 17, math.inf
        return (0, math.inf)

    def load_custom_items_file(self, silent: bool = False):
        path = self.custom_file_var.get().strip()
        if not path:
            if not silent:
                self.custom_status_var.set("No file specified")
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            parsed_tables: Dict[str, List[str]] = {}
            global_extras: List[str] = []
            cr_scoped: List[Tuple[Tuple[float, float], str]] = []

            if isinstance(data, dict):
                for key, value in data.items():
                    up_key = str(key).upper()
                    if up_key == "GLOBAL" and isinstance(value, list):
                        global_extras = [str(x).strip() for x in value if str(x).strip()]
                    elif up_key == "CR_SCOPED" and isinstance(value, list):
                        for entry in value:
                            if isinstance(entry, dict) and "range" in entry and "item" in entry:
                                rng = entry["range"]
                                item = str(entry["item"]).strip()
                                if isinstance(rng, (list, tuple)) and len(rng) == 2 and item:
                                    try:
                                        low = float(rng[0])
                                        high = float(rng[1])
                                        cr_scoped.append(((low, high), item))
                                    except Exception:
                                        continue
                    elif isinstance(value, list):
                        items = [str(x).strip() for x in value if str(x).strip()]
                        if items:
                            parsed_tables[up_key] = items
            elif isinstance(data, list):
                items = [str(x).strip() for x in data if str(x).strip()]
                if items:
                    parsed_tables["A"] = items

            self.custom_tables = {k: v for k, v in parsed_tables.items() if k not in ("GLOBAL", "CR_SCOPED")}
            self.manual_items_by_table = {k: list(v) for k, v in parsed_tables.items() if k in "ABCDEFGHI"}
            self.manual_items_by_cr = cr_scoped
            # Populate global text box
            self.manual_text.delete("1.0", tk.END)
            if global_extras:
                self.manual_text.insert(tk.END, "\n".join(global_extras))

            if not silent:
                if parsed_tables or global_extras or cr_scoped:
                    tables = ", ".join(sorted(parsed_tables.keys())) if parsed_tables else "none"
                    self.custom_status_var.set(f"Loaded (tables: {tables})")
                else:
                    self.custom_status_var.set("File read, no items found")
        except Exception as exc:  # pragma: no cover - GUI feedback
            if not silent:
                self.custom_status_var.set(f"Error: {exc}")

    def add_scoped_item(self):
        item = self.scoped_item_var.get().strip()
        table = self.scoped_table_var.get().upper()
        band = self.scoped_cr_var.get()
        if not item:
            self.scoped_status.set("No item text")
            return
        cr_range = self._parse_cr_band(band)
        if table == "ALL":
            self.manual_items_by_cr.append((cr_range, item))
        else:
            self.manual_items_by_table.setdefault(table, []).append(item)
            if cr_range != (0, math.inf):
                # Keep a CR filter for table-scoped too by encoding in manual_items_by_cr
                self.manual_items_by_cr.append((cr_range, item))
        self.scoped_item_var.set("")
        self.scoped_status.set("Added")
        # Auto-save to persist between runs
        self.save_custom_items_file(auto=True)

    def save_custom_items_file(self, auto: bool = False):
        path = self.custom_file_var.get().strip() or "custom_items.json"
        payload: Dict[str, List[str]] = {}
        # Table-scoped items from file + manual additions
        for tbl, items in self.manual_items_by_table.items():
            payload.setdefault(tbl, []).extend(items)
        for tbl, items in self.custom_tables.items():
            payload.setdefault(tbl, []).extend(items)
        # Global extras
        global_extras = self._manual_items()
        if global_extras:
            payload.setdefault("GLOBAL", []).extend(global_extras)
        # CR-scoped items
        if self.manual_items_by_cr:
            payload["CR_SCOPED"] = [
                {"range": list(rng), "item": item} for rng, item in self.manual_items_by_cr
            ]
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
            if not auto:
                self.save_status.set(f"Saved to {path}")
        except Exception as exc:  # pragma: no cover - GUI feedback
            if not auto:
                self.save_status.set(f"Error: {exc}")


def main():
    root = tk.Tk()
    LootApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
