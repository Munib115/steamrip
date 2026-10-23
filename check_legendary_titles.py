import sqlite3

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()

# Check titles matching legendary keywords
keywords = [
    "grand theft auto", "gta", "cyberpunk", "witcher", "red dead", "elden ring", "dark souls",
    "sekiro", "bloodborne", "god of war", "spider-man", "ghost of tsushima", "last of us",
    "horizon", "uncharted", "days gone", "call of duty", "battlefield", "halo", "forza",
    "assassin", "far cry", "watch dogs", "rainbow six", "splinter cell", "ghost recon",
    "division", "resident evil", "silent hill", "monster hunter", "devil may cry", "fallout",
    "elder scrolls", "skyrim", "starfield", "doom", "wolfenstein", "dishonored", "bioshock",
    "half-life", "portal", "left 4 dead", "dead space", "mass effect", "titanfall", "star wars jedi",
    "need for speed", "burnout", "forza horizon", "beamng", "palworld", "baldur", "hades",
    "hollow knight", "dead cells", "celeste", "subnautica", "stardew valley", "terraria",
    "outer wilds", "disco elysium", "sea of stars", "nier", "final fantasy", "persona",
    "yakuza", "like a dragon", "kingdom come", "mount & blade", "crusader kings", "civilization",
    "cities: skylines", "euro truck", "rust", "sons of the forest", "project zomboid", "valheim",
    "manor lords", "helldivers", "lethal company", "phasmophobia", "ready or not", "payday",
    "hitman", "tomb raider", "batman: arkham", "middle-earth", "metro", "s.t.a.l.k.e.r.",
    "dying light", "dead island", "control", "alan wake", "max payne", "mafia", "sleeping dogs",
    "borderlands", "deus ex", "prey", "death stranding", "metal gear", "armored core"
]

all_matched_ids = set()
for kw in keywords:
    c.execute("SELECT id, title, slug FROM games WHERE lower(title) LIKE ? AND is_active = 1", (f"%{kw}%",))
    rows = c.fetchall()
    for r in rows:
        all_matched_ids.add((r[0], r[1], r[2], kw))

print(f"Total top games matching legendary keywords: {len(all_matched_ids)}")
