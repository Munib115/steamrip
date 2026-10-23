import sqlite3

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()

# 1. Add top_rank column if not exists
try:
    c.execute("ALTER TABLE games ADD COLUMN top_rank INTEGER DEFAULT NULL")
    print("Added top_rank column to games table.")
except Exception as e:
    print("Column top_rank may already exist:", e)

# 2. Priority top AAA blockbuster slugs / keywords to rank 1..50
PRIORITY_SLUGS = [
    "grand-theft-auto-v-enhanced-free-download",
    "cyberpunk-2077-free-download",
    "red-dead-redemption-2-free-download-15",
    "grand-theft-auto-iv-free-download",
    "elden-ring-de-free-download-1gg",
    "call-of-duty-black-ops-6-free-download",
    "call-of-duty-black-ops-cold-war-free-download",
    "call-of-duty-modern-warfare-2-free-download-18",
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
    "assassins-creed-mirage-free-download-2o",
    "assassins-creed-valhalla-free-download-3s",
    "assassins-creed-black-flag-resynced-free-download",
    "assassins-creed-odyssey-free-download-4c",
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
    "resident-evil-4-ultimate-hd-edition-free-download",
    "silent-hill-2-free-download-18",
    "need-for-speed-most-wanted-black-edition-free-download-o1",
    "4-tom-clancys-rainbow-six-siege-complete-free-download-1h",
    "tom-clancys-splinter-cell-blacklist-free-download",
    "call-of-duty-black-ops-ii-free-download-4e",
    "call-of-duty-black-ops-4-free-download",
    "ready-or-not-free-download",
]

# Set priority ranks
rank = 1
for slug in PRIORITY_SLUGS:
    # Match exact or prefix
    base = slug.rsplit('-', 1)[0]
    c.execute("SELECT id, title, slug FROM games WHERE slug = ? OR slug LIKE ?", (slug, f"{base}%"))
    rows = c.fetchall()
    if rows:
        gid, title, gslug = rows[0]
        c.execute("UPDATE games SET top_rank = ? WHERE id = ?", (rank, gid))
        print(f"Rank {rank:2d}: [{gid}] {title[:40]} ({gslug})")
        rank += 1

# Also rank remaining games crawled from SteamRIP's /top-games/
from scratch_check_top_missing import all_top
for slug, href, title in all_top:
    base = slug.rsplit('-', 1)[0]
    c.execute("SELECT id FROM games WHERE (slug = ? OR slug LIKE ?) AND top_rank IS NULL", (slug, f"{base}%"))
    row = c.fetchone()
    if row:
        c.execute("UPDATE games SET top_rank = ? WHERE id = ?", (rank, row[0]))
        rank += 1

conn.commit()
c.execute("SELECT COUNT(*) FROM games WHERE top_rank IS NOT NULL")
print(f"\nTotal games with top_rank assigned: {c.fetchone()[0]}")
conn.close()
