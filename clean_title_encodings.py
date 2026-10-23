import sqlite3

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()

c.execute("SELECT id, title FROM games WHERE title LIKE '%\ufffd%'")
bad_titles = c.fetchall()
print(f"Found {len(bad_titles)} titles with replacement character \\ufffd")

for gid, title in bad_titles[:15]:
    # In most cases, the replacement char is an apostrophe (Assassin's Creed, Marvel's Spider-Man, Baldur's Gate, Director's Cut)
    # or dash or special letter (Ragnarok, Pokemon)
    fixed = title
    if "Assassin" in fixed:
        fixed = fixed.replace("\ufffd", "'")
    elif "Marvel" in fixed or "Baldur" in fixed or "Director" in fixed or "Witch" in fixed or "King" in fixed or "That" in fixed:
        fixed = fixed.replace("\ufffd", "'")
    elif "Ragnar" in fixed:
        fixed = fixed.replace(f"Ragnar\ufffdk", "Ragnarok")
    elif "\ufffd" in fixed:
        fixed = fixed.replace("\ufffd", "'")
    print(f"  [{gid}] {title} -> {fixed}")

# Update all games where \ufffd exists
fixed_count = 0
for gid, title in bad_titles:
    fixed = title
    # Specific known fixes
    fixed = fixed.replace("Ragnar\ufffdk", "Ragnarok")
    fixed = fixed.replace("Pok\ufffdmon", "Pokemon")
    fixed = fixed.replace("Pok\ufffd", "Poke")
    fixed = fixed.replace("\ufffd", "'")
    if fixed != title:
        c.execute("UPDATE games SET title = ? WHERE id = ?", (fixed, gid))
        fixed_count += 1

conn.commit()
print(f"Successfully cleaned {fixed_count} titles in database!")
