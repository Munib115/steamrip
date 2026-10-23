import sqlite3
from pathlib import Path

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()

c.execute("""
    SELECT g.id, g.top_rank, g.title, g.slug, g.thumbnail_url, COUNT(f.id)
    FROM games g
    LEFT JOIN game_files f ON g.id = f.game_id
    WHERE g.top_rank IS NOT NULL
    GROUP BY g.id
    ORDER BY g.top_rank ASC
""")
top_games = c.fetchall()

print(f"Total top ranked games checked: {len(top_games)}")

missing_posters = []
missing_files = []
root_posters = Path("posters")
backend_posters = Path("backend/posters")

for gid, rank, title, slug, thumb, file_count in top_games:
    p1 = root_posters / f"{slug}.jpg"
    p2 = backend_posters / f"{slug}.jpg"
    if not p1.exists() or not p2.exists():
        missing_posters.append((gid, rank, title, slug))
    if file_count == 0:
        missing_files.append((gid, rank, title, slug))

print(f"Games with missing local poster files: {len(missing_posters)}")
print(f"Games with 0 download mirrors: {len(missing_files)}")

if missing_posters:
    print("\nMissing posters sample:")
    for m in missing_posters[:10]:
        print(f"  Rank #{m[1]}: [{m[0]}] {m[2]} ({m[3]})")

if missing_files:
    print("\nMissing files sample:")
    for m in missing_files[:10]:
        print(f"  Rank #{m[1]}: [{m[0]}] {m[2]} ({m[3]})")
