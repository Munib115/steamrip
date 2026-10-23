import sqlite3
import re

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()

# Ensure top_rank column exists
try:
    c.execute("ALTER TABLE games ADD COLUMN top_rank INTEGER DEFAULT NULL")
except Exception:
    pass

# Clear existing top_ranks to do a clean 1..1000 ranking
c.execute("UPDATE games SET top_rank = NULL")
conn.commit()

# Tier 1: Absolute Blockbuster AAA Titles (1..50)
TIER_1_SLUGS = [
    "grand-theft-auto-v-enhanced-free-download",
    "cyberpunk-2077-free-download",
    "red-dead-redemption-2-free-download-15",
    "grand-theft-auto-iv-free-download",
    "elden-ring-de-free-download-1gg",
    "call-of-duty-black-ops-6-free-download",
    "call-of-duty-black-ops-cold-war-free-download",
    "call-of-duty-modern-warfare-2-free-download-13",
    "call-of-duty-modern-warfare-4-free-download",
    "marvels-spider-man-2-free-download-sp1",
    "marvels-spider-man-remastered-free-download",
    "god-of-war-ragnarok-free-download-r2",
    "god-of-war-free-download",
    "ghost-of-tsushima-free-download",
    "black-myth-wukong-free-download",
    "the-last-of-us-part-one-free-download-3r",
    "forza-horizon-5-premium-edition-free-download-r3",
    "forza-horizon-6-free-download",
    "beamng-drive-free-download-3e",
    "palworld-free-download-2p",
    "gta-san-andreas-free-download-1i",
    "grand-theft-auto-iii-free-download",
    "assassins-creed-mirage-free-download",
    "assassins-creed-valhalla-free-download-3s",
    "assassins-creed-black-flag-resynced-free-download",
    "assassins-creed-odyssey-free-download-13",
    "assassins-creed-shadows-free-download",
    "far-cry-6-ultimate-edition-free-download-z1",
    "far-cry-5-gold-edition-free-download-1f",
    "far-cry-4-gold-edition-free-download-o2",
    "far-cry-3-free-download-s2",
    "watch-dogs-2-free-download-p5",
    "watch-dogs-legion-free-download-w5",
    "the-witcher-3-wild-hunt-r-free-download-v8a",
    "baldur-s-gate-3-free-download-u2",
    "red-dead-redemption-free-download",
    "horizon-forbidden-west-complete-edition-free-download",
    "horizon-zero-dawn-complete-edition-free-download",
    "dying-light-2-stay-human-free-download",
    "starfield-free-download-1u",
    "fallout-4-free-download-4x",
    "the-elder-scrolls-v-skyrim-se-free-download-t3",
    "sekiro-shadows-die-twice-free-download-c2",
    "dark-souls-iii-free-download-17",
    "resident-evil-4-ultimate-hd-edition-free-download-1m",
    "silent-hill-2-free-download",
    "need-for-speed-most-wanted-black-edition-free-download-o1",
    "4-tom-clancys-rainbow-six-siege-complete-free-download-1h",
    "tom-clancys-splinter-cell-blacklist-free-download",
    "call-of-duty-black-ops-ii-free-download-4e",
    "call-of-duty-black-ops-4-free-download",
    "ready-or-not-free-download",
]

ranked_ids = set()
current_rank = 1

def assign_rank(game_id, reason=""):
    global current_rank
    if game_id not in ranked_ids and current_rank <= 1000:
        # Verify game has at least 1 file
        c.execute("SELECT COUNT(*) FROM game_files WHERE game_id = ?", (game_id,))
        if c.fetchone()[0] == 0:
            return False
        c.execute("UPDATE games SET top_rank = ? WHERE id = ?", (current_rank, game_id))
        ranked_ids.add(game_id)
        current_rank += 1
        return True
    return False

# 1. Assign Tier 1
for slug in TIER_1_SLUGS:
    base = slug.rsplit('-', 1)[0]
    c.execute("SELECT id, title FROM games WHERE slug = ? OR slug LIKE ?", (slug, f"{base}%"))
    row = c.fetchone()
    if row:
        assign_rank(row[0], f"Tier 1: {row[1]}")

print(f"Ranked {len(ranked_ids)} Tier 1 blockbusters")

# 2. SteamRIP Top Games list (from cached steamrip_top_games.json)
import json
with open('steamrip_top_games.json', 'r') as f:
    steamrip_top = json.load(f)

for slug in steamrip_top:
    base = slug.rsplit('-', 1)[0]
    c.execute("SELECT id, title FROM games WHERE slug = ? OR slug LIKE ?", (slug, f"{base}%"))
    for row in c.fetchall():
        assign_rank(row[0], f"SteamRIP Top: {row[1]}")

print(f"Ranked up to {len(ranked_ids)} after SteamRIP /top-games/ catalog")

# 3. Major Franchises (Call of Duty, Assassin's Creed, Far Cry, Resident Evil, etc.)
FRANCHISE_KEYWORDS = [
    "call of duty", "assassin's creed", "far cry", "grand theft auto", "gta",
    "red dead", "spider-man", "god of war", "resident evil", "silent hill",
    "battlefield", "fallout", "elder scrolls", "skyrim", "dark souls", "elden ring",
    "need for speed", "forza", "watch dogs", "tom clancy", "rainbow six",
    "splinter cell", "ghost recon", "division", "witcher", "cyberpunk",
    "tomb raider", "batman", "hitman", "halo", "mass effect", "dead space",
    "dishonored", "bioshock", "wolfenstein", "doom", "borderlands", "metro",
    "mafia", "max payne", "alan wake", "control", "dying light", "yakuza",
    "like a dragon", "final fantasy", "persona", "monster hunter", "devil may cry",
    "metal gear", "kingdom come", "hollow knight", "hades", "balatro", "palworld",
    "subnautica", "stardew valley", "rust", "sons of the forest", "project zomboid",
    "valheim", "lethal company", "phasmophobia", "cities: skylines", "civilization",
    "beamng", "euro truck", "sea of stars", "nier", "dead cells", "celeste", "outer wilds"
]

for kw in FRANCHISE_KEYWORDS:
    if current_rank > 1000:
        break
    c.execute(
        "SELECT id, title FROM games WHERE lower(title) LIKE ? AND is_active = 1 AND top_rank IS NULL ORDER BY id ASC",
        (f"%{kw}%",)
    )
    for row in c.fetchall():
        if current_rank > 1000:
            break
        assign_rank(row[0], f"Franchise ({kw}): {row[1]}")

print(f"Ranked up to {len(ranked_ids)} after major franchise sweep")

# 4. Fill remaining spots up to 1000 with the best reviewed / largest / top games in database
if current_rank <= 1000:
    # Prioritize games that have game_files and description, ordered by id asc or updated
    c.execute("""
        SELECT g.id, g.title
        FROM games g
        JOIN game_files f ON g.id = f.game_id
        WHERE g.is_active = 1 AND g.top_rank IS NULL
        GROUP BY g.id
        HAVING COUNT(f.id) >= 1
        ORDER BY g.id ASC
    """)
    for row in c.fetchall():
        if current_rank > 1000:
            break
        assign_rank(row[0], f"Popular general: {row[1]}")

conn.commit()

c.execute("SELECT COUNT(*) FROM games WHERE top_rank IS NOT NULL")
total_ranked = c.fetchone()[0]
print(f"\nFinal count of top ranked games: {total_ranked}")

print("\nSample of Top Ranked Games (1..20 and 990..1000):")
c.execute("SELECT top_rank, title, slug FROM games WHERE top_rank IS NOT NULL ORDER BY top_rank ASC LIMIT 20")
for r in c.fetchall():
    print(f"  #{r[0]:4d}: {r[1][:50]} ({r[2]})")

c.execute("SELECT top_rank, title, slug FROM games WHERE top_rank IS NOT NULL ORDER BY top_rank DESC LIMIT 10")
for r in reversed(c.fetchall()):
    print(f"  #{r[0]:4d}: {r[1][:50]} ({r[2]})")

conn.close()
