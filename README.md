# TBC Warrior Gear Combo PoC

This proof of concept brute-forces warrior gear combinations, prints stats for every modeled gear option, and ranks combinations by weighted score.

## Modeled options

- **Head**
  - Gladiator's Plate Helm
  - Helm of the Claw
  - Furious Gizmatic Goggles
- **Neck**
  - Choker of Vile Intent
- **Shoulder**
  - Warbringer Shoulderplates
- **Back**
  - Cloak of the Inciter
  - Cloak of the Pit Stalker
- **Chest**
  - Gladiator's Plate Chestpiece
  - Destroyer Breastplate
- **Wrist**
  - Bladespire Warbands
- **Hands**
  - Gauntlets of Martial Perfection
- **Waist**
  - Deathforge Girdle
  - Red Belt of Battle
- **Legs**
  - Skulker's Greaves
  - Greaves of the Bloodwarder
- **Feet**
  - Ironstriders of Urgency
  - Fel Leather Boots
- **Mainhand**
  - Gladiator's Cleaver
- **Finger (2 slots)**
  - Ring of Arathi Warlords
  - Mithril Band of the Unscarred
  - Violet Signet of the Master Assassin
- **Head Enchant**
  - Glyph of Ferocity (+34 Attack Power, +16 Hit Rating)
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

Edit `constraints` in `main()` (treated as minimum values). The current default is 142 hit rating. Running `python3 gear_optimizer.py` also exports the top results to `top_results.md`:

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


## Output

- Running the script now prints full stats for all gear pieces first.
- The optimizer calculates and prints the top 30 combinations by score.
- A sample Top 30 markdown export is stored in `top_results.md`.
