import sqlite3
from pathlib import Path

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM games')
total = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM games WHERE top_rank IS NOT NULL')
top_ranked = c.fetchone()[0]

c.execute('SELECT COUNT(DISTINCT game_id) FROM game_files')
with_files = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM games WHERE thumbnail_url LIKE '/posters/%'")
with_local_posters = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM games WHERE description IS NOT NULL AND length(description) > 30")
with_desc = c.fetchone()[0]

print(f"Total games in DB: {total}")
print(f"Games with top_rank assigned: {top_ranked}")
print(f"Games with download mirrors: {with_files}")
print(f"Games with local /posters/ URL: {with_local_posters}")
print(f"Games with rich description: {with_desc}")

# Count physical poster files on disk
posters_dir = Path("posters")
backend_posters = Path("backend/posters")
disk_posters = len(list(posters_dir.glob("*.jpg")))
backend_disk_posters = len(list(backend_posters.glob("*.jpg")))
print(f"Physical poster files in posters/: {disk_posters}")
print(f"Physical poster files in backend/posters/: {backend_disk_posters}")
