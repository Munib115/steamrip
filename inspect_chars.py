import sqlite3

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()
c.execute("SELECT id, title FROM games WHERE id = 271")
row = c.fetchone()
print("ID 271 title:", repr(row[1]))
for ch in row[1]:
    if ord(ch) > 127:
        print(f"Non-ascii char: {repr(ch)}, ord={ord(ch)}, hex={hex(ord(ch))}")
