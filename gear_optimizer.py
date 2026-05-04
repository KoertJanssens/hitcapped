#!/usr/bin/env python3
"""PoC optimizer for TBC warrior gear combinations."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple

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
        Item("Warbringer Shoulderplates", "shoulder", {"strength": 24, "critRating": 17, "hitRating": 15}),
    ],
    "back": [
        Item("Cloak of the Inciter", "back", {"agility": 21, "attackPower": 42, "hitRating": 16}),
    ],
    "chest": [
        Item("Gladiator's Plate Chestpiece", "chest", {"strength": 33, "critRating": 24}, sockets=2),
    ],
    "wrist": [
        Item("Bladespire Warbands", "wrist", {"strength": 17, "critRating": 16, "hitRating": 12}),
    ],
    "hands": [
        Item("Gauntlets of Martial Perfection", "hands", {"strength": 29, "critRating": 19, "hitRating": 20}, sockets=1),
    ],
    "waist": [
        Item("Deathforge Girdle", "waist", {"strength": 26, "critRating": 16}, sockets=1),
    ],
    "legs": [
        Item("Skulker's Greaves", "legs", {"agility": 34, "attackPower": 84}, sockets=3),
    ],
    "feet": [
        Item("Ironstriders of Urgency", "feet", {"strength": 24, "critRating": 20, "hitRating": 16}),
    ],
    "ranged": [
        Item("Xavian Stiletto", "ranged", {"agility": 16, "attackPower": 30, "hitRating": 11}),
        Item("Mama's Insurance", "ranged", {"agility": 20, "attackPower": 42, "critRating": 14}),
    ],
}

RING_OPTIONS: List[Item] = [
    Item("Ring of Arathi Warlords", "finger", {"strength": 20, "attackPower": 40, "hitRating": 18}),
    Item("Mithril Band of the Unscarred", "finger", {"strength": 22, "attackPower": 44, "critRating": 20}),
    Item("Violet Signet of the Master Assassin", "finger", {"agility": 22, "attackPower": 40, "hitRating": 19}),
]

FOOD_OPTIONS: List[FoodBuff] = [
    FoodBuff(name="Roasted Clefthoof (+20 Strength)", stats={"strength": 20}),
    FoodBuff(name="Spicy Hot Talbuk (+20 Hit Rating)", stats={"hitRating": 20}),
]


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


def optimize(constraints: Dict[str, int] | None = None, top_n: int = 10) -> List[Dict]:
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
                                                                "gems": gems_label,
                                                                "stats": gear_stats,
                                                                "score": round(score(gear_stats, STAT_WEIGHTS), 3),
                                                                }
                                                            )

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]


def main() -> None:
    constraints = {"hitRating": 142}
    best = optimize(constraints=constraints, top_n=20)

    print("=== Top combinations ===")
    print(f"Constraints: {constraints}\n")

    if not best:
        print("No combos meet the constraints.")
        return

    for idx, combo in enumerate(best, start=1):
        print(f"{idx}. score={combo['score']}")
        for slot in [
            "head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet", "ranged", "finger1", "finger2", "food", "gems"
        ]:
            print(f"   {slot}: {combo[slot]}")
        print(f"   stats: {combo['stats']}")
        print()


if __name__ == "__main__":
    main()
