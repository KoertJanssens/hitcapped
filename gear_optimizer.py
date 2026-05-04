#!/usr/bin/env python3
"""PoC optimizer for TBC warrior gear combinations."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple
import argparse

STAT_WEIGHTS: Dict[str, float] = {
    "strength": 2.2,
    "agility": 1.625,
    "attackPower": 1,
    "hitRating": 1.15,
    "critRating": 2.21,
    "hasteRating": 1.868,
    "armorPen": 0.32,
    "expertiseRating": 2.98,
    "metaSockets": 100,
}


@dataclass(frozen=True)
class Item:
    name: str
    slot: str
    stats: Dict[str, int]
    sockets: int = 0
    meta_sockets: int = 0


@dataclass(frozen=True)
class FoodBuff:
    name: str
    stats: Dict[str, int]


GEMS = {
    "8_str": {"strength": 8},
    "8_hit": {"hitRating": 8},
    "4_agi_4_hit": {"agility": 4, "hitRating": 4},
}

# NOTE: Stats were seeded from TBC database pages for PoC use.
SLOT_OPTIONS: Dict[str, List[Item]] = {
    "head": [
        Item("Gladiator's Plate Helm", "head", {"strength": 30, "critRating": 28}, sockets=1, meta_sockets=1),
        Item("Helm of the Claw", "head", {"agility": 25, "hitRating": 14, "attackPower": 66}, sockets=1, meta_sockets=1),
    ],
    "neck": [
        Item("Choker of Vile Intent", "neck", {"agility": 20, "hitRating": 18, "attackPower": 42}),
    ],
    "shoulder": [
        Item("Warbringer Shoulderplates", "shoulder", {"strength": 32, "agility": 22, "hitRating": 13}),
    ],
    "back": [
        Item("Cloak of the Inciter", "back", {"attackPower": 30, "hitRating": 16, "critRating": 18}),
    ],
    "chest": [
        Item("Gladiator's Plate Chestpiece", "chest", {"strength": 23, "hitRating": 12, "critRating": 30}, sockets=2),
    ],
    "wrist": [
        Item("Bladespire Warbands", "wrist", {"strength": 20, "critRating": 24}),
    ],
    "hands": [
        Item("Gauntlets of Martial Perfection", "hands", {"strength": 36, "critRating": 23}, sockets=1),
    ],
    "waist": [
        Item("Deathforge Girdle", "waist", {"strength": 22, "critRating": 20}, sockets=1),
    ],
    "legs": [
        Item("Skulker's Greaves", "legs", {"agility": 32, "attackPower": 64, "hitRating": 28}, sockets=3),
    ],
    "feet": [
        Item("Ironstriders of Urgency", "feet", {"strength": 33, "agility": 20}),
    ],
    "ranged": [
        Item("Xavian Stiletto", "ranged", {"hitRating": 12, "critRating": 20}),
        Item("Mama's Insurance", "ranged", {"agility": 10, "attackPower": 32, "critRating": 6}),
    ],
}

RING_OPTIONS: List[Item] = [
    Item("Ring of Arathi Warlords", "finger", {"attackPower": 46, "critRating": 23}),
    Item("Mithril Band of the Unscarred", "finger", {"strength": 26, "critRating": 22}),
    Item("Violet Signet of the Master Assassin", "finger", {"attackPower": 56, "hitRating": 25}),
]



# Wowhead TBC item IDs are required for fetch_wowhead_item_stats(item_id).
# Fill this map as you verify IDs from Wowhead URLs (item=<id>). 
ITEM_ID_BY_NAME: Dict[str, int] = {
    "Gladiator's Plate Helm": 24545,
    "Helm of the Claw": 28182,
    "Choker of Vile Intent": 29381,
    "Warbringer Shoulderplates": 29023,
    "Cloak of the Inciter": 27892,
    "Gladiator's Plate Chestpiece": 24544,
    "Bladespire Warbands": 28795,
    "Gauntlets of Martial Perfection": 28824,
    "Deathforge Girdle": 27985,
    "Skulker's Greaves": 28741,
    "Ironstriders of Urgency": 28608,
    "Xavian Stiletto": 28659,
    "Mama's Insurance": 30279,
    "Ring of Arathi Warlords": 29379,
    "Mithril Band of the Unscarred": 28730,
    "Violet Signet of the Master Assassin": 29283,
}
HEAD_ENCHANT = {"name": "Glyph of Ferocity (+34 Attack Power, +16 Hit Rating)", "stats": {"attackPower": 34, "hitRating": 16}}

FOOD_OPTIONS: List[FoodBuff] = [
    FoodBuff(name="Roasted Clefthoof (+20 Strength)", stats={"strength": 20}),
    FoodBuff(name="Spicy Hot Talbuk (+20 Hit Rating)", stats={"hitRating": 20}),
]




def build_item_stats_index() -> Dict[str, Dict[str, int]]:
    """Build a lookup of item name -> base item stats from modeled gear options."""
    index: Dict[str, Dict[str, int]] = {}
    for items in SLOT_OPTIONS.values():
        for item in items:
            index[item.name] = dict(item.stats)
    for item in RING_OPTIONS:
        index[item.name] = dict(item.stats)
    return index


def get_item_stats(item_name: str) -> Dict[str, int]:
    """Return hardcoded modeled stats for an item name."""
    item_stats_index = build_item_stats_index()
    if item_name not in item_stats_index:
        raise KeyError(f"Unknown item '{item_name}'. Add it to SLOT_OPTIONS or RING_OPTIONS first.")
    return item_stats_index[item_name]




def all_modeled_item_names() -> List[str]:
    names: List[str] = []
    for items in SLOT_OPTIONS.values():
        names.extend(item.name for item in items)
    names.extend(item.name for item in RING_OPTIONS)
    return names


def verify_modeled_items_have_stats() -> List[str]:
    """Verify every modeled item is retrievable through get_item_stats()."""
    missing_or_empty: List[str] = []
    for item_name in all_modeled_item_names():
        stats = get_item_stats(item_name)
        if not stats:
            missing_or_empty.append(item_name)
    return missing_or_empty



def verify_modeled_items_have_wowhead_ids() -> List[str]:
    """Return modeled item names that do not have a known Wowhead item ID yet."""
    return [name for name in all_modeled_item_names() if name not in ITEM_ID_BY_NAME]

def parse_wowhead_item_stats(html: str) -> Dict[str, int]:
    """Parse a TBC Wowhead item payload and extract selected combat stats."""
    import re

    stats: Dict[str, int] = {}

    json_equip_match = re.search(r"<jsonEquip><!\[CDATA\[(.*?)\]\]></jsonEquip>", html, flags=re.IGNORECASE | re.DOTALL)
    if json_equip_match:
        json_equip = json_equip_match.group(1)
        json_patterns = {
            "strength": r'"str":(\d+)',
            "agility": r'"agi":(\d+)',
            "attackPower": r'"mleatkpwr":(\d+)',
            "hitRating": r'"mlehitrtng":(\d+)',
            "critRating": r'"mlecritstrkrtng":(\d+)',
            "hasteRating": r'"hastertng":(\d+)',
            "expertiseRating": r'"exprtng":(\d+)',
            "armorPen": r'"armorpenrtng":(\d+)',
        }
        for stat_name, pattern in json_patterns.items():
            match = re.search(pattern, json_equip, flags=re.IGNORECASE)
            if match:
                stats[stat_name] = int(match.group(1))

    if stats:
        return stats

    patterns = {
        "strength": r"\+(\d+) Strength",
        "agility": r"\+(\d+) Agility",
        "attackPower": r"Increases attack power by (\d+)\.?",
        "hitRating": r"Improves (?:your )?hit rating by (\d+)\.?",
        "critRating": r"Improves (?:your )?critical strike rating by (\d+)\.?",
        "hasteRating": r"Improves (?:your )?haste rating by (\d+)\.?",
        "expertiseRating": r"Increases your expertise rating by (\d+)\.?",
        "armorPen": r"Your attacks ignore (\d+) of your opponent's armor",
    }

    for stat_name, pattern in patterns.items():
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if match:
            stats[stat_name] = int(match.group(1))
    return stats


def fetch_wowhead_item_stats(item_id: int) -> Dict[str, int]:
    """Fetch and parse item stats from Wowhead TBC for hardcoding into this PoC."""
    from urllib.error import URLError
    from urllib.request import Request, urlopen

    url = f"https://www.wowhead.com/tbc/item={item_id}&xml"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urlopen(req, timeout=20) as response:
            html = response.read().decode("utf-8", errors="replace")
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch Wowhead item page: {url}") from exc

    stats = parse_wowhead_item_stats(html)
    if not stats:
        raise ValueError(f"No supported stats parsed from Wowhead page: {url}")
    return stats




def verify_modeled_items_against_wowhead(delay_seconds: float = 1.0) -> Tuple[List[str], List[str]]:
    """Compare modeled stats against parsed Wowhead stats with throttling between requests."""
    import time

    mismatches: List[str] = []
    errors: List[str] = []

    for item_name in all_modeled_item_names():
        item_id = ITEM_ID_BY_NAME.get(item_name)
        if item_id is None:
            errors.append(f"{item_name}: missing Wowhead item ID")
            continue

        time.sleep(delay_seconds)

        try:
            wowhead_stats = fetch_wowhead_item_stats(item_id)
        except Exception as exc:  # network/parse failures are surfaced in output
            errors.append(f"{item_name} (id={item_id}): {exc}")
            continue

        modeled_stats = get_item_stats(item_name)
        relevant_stats = set(modeled_stats) | set(wowhead_stats)
        for stat_name in relevant_stats:
            stat_value = wowhead_stats.get(stat_name, 0)
            modeled_value = modeled_stats.get(stat_name, 0)
            if modeled_value != stat_value:
                mismatches.append(
                    f"{item_name} (id={item_id}) {stat_name}: modeled={modeled_value}, wowhead={stat_value}"
                )

    return mismatches, errors

def merge_stats(*stat_maps: Dict[str, int]) -> Dict[str, int]:
    merged: Dict[str, int] = {}
    for stats in stat_maps:
        for k, v in stats.items():
            merged[k] = merged.get(k, 0) + v
    return merged


def score(stats: Dict[str, int], weights: Dict[str, float]) -> float:
    return sum(stats.get(stat, 0) * weights.get(stat, 0.0) for stat in weights)


def meets_constraints(stats: Dict[str, int], constraints: Dict[str, int]) -> bool:
    return all(stats.get(stat, 0) >= minimum for stat, minimum in constraints.items())


def gem_allocations(num_sockets: int) -> List[Tuple[str, Dict[str, int]]]:
    """Return unique gem-count allocations (not permutations)."""
    if num_sockets == 0:
        return [("no_gems", {})]

    gem_names = list(GEMS.keys())
    allocations: List[Tuple[str, Dict[str, int]]] = []

    def build(idx: int, remaining: int, counts: Dict[str, int]) -> None:
        if idx == len(gem_names) - 1:
            counts[gem_names[idx]] = remaining

            total: Dict[str, int] = {}
            for gem_name, count in counts.items():
                if count:
                    total = merge_stats(total, {k: v * count for k, v in GEMS[gem_name].items()})

            label = ", ".join(f"{name}x{counts[name]}" for name in gem_names if counts.get(name, 0))
            allocations.append((label, total))
            return

        gem = gem_names[idx]
        for n in range(remaining + 1):
            counts[gem] = n
            build(idx + 1, remaining - n, counts)

    build(0, num_sockets, {})
    return allocations


def optimize(constraints: Dict[str, int] | None = None, top_n: int = 30) -> List[Dict]:
    constraints = constraints or {}
    results = []

    ring_pairs = list(combinations(RING_OPTIONS, 2))  # 2 finger slots

    for head in SLOT_OPTIONS["head"]:
        for neck in SLOT_OPTIONS["neck"]:
            for shoulder in SLOT_OPTIONS["shoulder"]:
                for back in SLOT_OPTIONS["back"]:
                    for chest in SLOT_OPTIONS["chest"]:
                        for wrist in SLOT_OPTIONS["wrist"]:
                            for hands in SLOT_OPTIONS["hands"]:
                                for waist in SLOT_OPTIONS["waist"]:
                                    for legs in SLOT_OPTIONS["legs"]:
                                        for feet in SLOT_OPTIONS["feet"]:
                                            for ranged in SLOT_OPTIONS["ranged"]:
                                                for ring1, ring2 in ring_pairs:
                                                    total_sockets = (
                                                    head.sockets
                                                    + neck.sockets
                                                    + shoulder.sockets
                                                    + back.sockets
                                                    + chest.sockets
                                                    + wrist.sockets
                                                    + hands.sockets
                                                    + waist.sockets
                                                    + legs.sockets
                                                    + feet.sockets
                                                    + ranged.sockets
                                                    + ring1.sockets
                                                    + ring2.sockets
                                                )
                                                    total_meta = (
                                                    head.meta_sockets
                                                    + neck.meta_sockets
                                                    + shoulder.meta_sockets
                                                    + back.meta_sockets
                                                    + chest.meta_sockets
                                                    + wrist.meta_sockets
                                                    + hands.meta_sockets
                                                    + waist.meta_sockets
                                                    + legs.meta_sockets
                                                    + feet.meta_sockets
                                                    + ranged.meta_sockets
                                                    + ring1.meta_sockets
                                                    + ring2.meta_sockets
                                                )

                                                    for food in FOOD_OPTIONS:
                                                        for gems_label, gem_stats in gem_allocations(total_sockets):
                                                            gear_stats = merge_stats(
                                                            head.stats,
                                                            neck.stats,
                                                            shoulder.stats,
                                                            back.stats,
                                                            chest.stats,
                                                            wrist.stats,
                                                            hands.stats,
                                                            waist.stats,
                                                            legs.stats,
                                                            feet.stats,
                                                            ranged.stats,
                                                            ring1.stats,
                                                            ring2.stats,
                                                            food.stats,
                                                            HEAD_ENCHANT["stats"],
                                                            gem_stats,
                                                            {"metaSockets": total_meta},
                                                        )
                                                            if not meets_constraints(gear_stats, constraints):
                                                                continue

                                                            results.append(
                                                                {
                                                                "head": head.name,
                                                                "neck": neck.name,
                                                                "shoulder": shoulder.name,
                                                                "back": back.name,
                                                                "chest": chest.name,
                                                                "wrist": wrist.name,
                                                                "hands": hands.name,
                                                                "waist": waist.name,
                                                                "legs": legs.name,
                                                                "feet": feet.name,
                                                                "ranged": ranged.name,
                                                                "finger1": ring1.name,
                                                                "finger2": ring2.name,
                                                                "food": food.name,
                                                                "head_enchant": HEAD_ENCHANT["name"],
                                                                "gems": gems_label,
                                                                "stats": gear_stats,
                                                                "score": round(score(gear_stats, STAT_WEIGHTS), 3),
                                                                }
                                                            )

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]




def print_all_gear_stats() -> None:
    print("=== All gear options and stats ===")
    for slot, items in SLOT_OPTIONS.items():
        print(f"\n[{slot}]")
        for item in items:
            print(f"- {item.name}: {item.stats} (sockets={item.sockets}, meta_sockets={item.meta_sockets})")
    print("\n[finger]")
    for item in RING_OPTIONS:
        print(f"- {item.name}: {item.stats} (sockets={item.sockets}, meta_sockets={item.meta_sockets})")
    print(f"\n[head_enchant]\n- {HEAD_ENCHANT['name']}: {HEAD_ENCHANT['stats']}")

def main(verify_stats: bool = False, verify_delay: float = 1.0) -> None:
    print_all_gear_stats()
    print()

    missing_or_empty = verify_modeled_items_have_stats()
    if missing_or_empty:
        print("WARNING: Some modeled items are missing stats:")
        for item_name in missing_or_empty:
            print(f"- {item_name}")
    else:
        print(f"Verified {len(all_modeled_item_names())} modeled items via get_item_stats().")

    missing_ids = verify_modeled_items_have_wowhead_ids()
    if missing_ids:
        print("WARNING: Missing Wowhead item IDs for:")
        for item_name in missing_ids:
            print(f"- {item_name}")
    else:
        print("All modeled items have Wowhead IDs.")

    if verify_stats:
        print("Verifying modeled stats against Wowhead (with request delay)...")
        mismatches, wowhead_errors = verify_modeled_items_against_wowhead(delay_seconds=verify_delay)
        if mismatches:
            print("WARNING: Stat mismatches found:")
            for row in mismatches:
                print(f"- {row}")
        else:
            print("No stat mismatches detected for parsed Wowhead stats.")

        if wowhead_errors:
            print("WARNING: Wowhead verification errors:")
            for row in wowhead_errors:
                print(f"- {row}")

        print("Verification mode enabled; skipping constraint optimization.")
        return
    else:
        print("Skipping Wowhead stat verification (use --verify-stats to enable).")

    constraints = {"hitRating": 142}
    best = optimize(constraints=constraints, top_n=30)

    print("=== Top 30 combinations ===")
    print(f"Constraints: {constraints}\n")

    if not best:
        print("No combos meet the constraints.")
        return

    for idx, combo in enumerate(best, start=1):
        print(f"{idx}. score={combo['score']}")
        for slot in [
            "head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet", "ranged", "finger1", "finger2", "food", "head_enchant", "gems"
        ]:
            print(f"   {slot}: {combo[slot]}")
        print(f"   stats: {combo['stats']}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize warrior gear combinations.")
    parser.add_argument("--verify-stats", action="store_true", default=False, help="Verify modeled stats against Wowhead before optimization.")
    parser.add_argument("--verify-delay", type=float, default=1.0, help="Delay in seconds between Wowhead verification requests.")
    args = parser.parse_args()
    main(verify_stats=args.verify_stats, verify_delay=args.verify_delay)
