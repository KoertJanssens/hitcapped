# TBC Warrior Gear Combo PoC

This proof of concept brute-forces warrior gear combinations and ranks them by weighted score.

## Modeled options

- **Head**
  - Gladiator's Plate Helm
  - Helm of the Claw
- **Neck**
  - Choker of Vile Intent
- **Shoulder**
  - Warbringer Shoulderplates
- **Back**
  - Cloak of the Inciter
- **Chest**
  - Gladiator's Plate Chestpiece
- **Wrist**
  - Bladespire Warbands
- **Hands**
  - Gauntlets of Martial Perfection
- **Waist**
  - Deathforge Girdle
- **Legs**
  - Skulker's Greaves
- **Feet**
  - Ironstriders of Urgency
- **Finger (2 slots)**
  - Ring of Arathi Warlords
  - Mithril Band of the Unscarred
  - Violet Signet of the Master Assassin
- **Food**
  - Roasted Clefthoof (+20 Strength)
  - Spicy Hot Talbuk (+20 Hit Rating)
- **Gem fill choices for regular sockets**
  - +8 Strength
  - +8 Hit Rating
  - +4 Agility / +4 Hit Rating

## Run

```bash
python3 gear_optimizer.py
```

## Constraints

Edit `constraints` in `main()` (treated as minimum values). The current default is 142 hit rating:

```python
constraints = {
    "hitRating": 142,
}
```

## Notes

- Ring combinations are generated as unique 2-ring pairs (`finger1` + `finger2`).
- Gem fills are generated as unique gem-count allocations (no duplicate permutation rows).
- `metaSockets` is included in weighted scoring.
- Item stats are seeded from TBC item database pages for PoC use.
