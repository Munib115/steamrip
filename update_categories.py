import sqlite3
from bs4 import BeautifulSoup

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()

# 1. Update from steamrip_home.html if present
try:
    with open('steamrip_home.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    cards = soup.find_all(class_=lambda cl: cl and 'post-item' in cl)
    for card in cards:
        link = card.find('a', href=True)
        if not link:
            continue
        slug = link['href'].strip('/').split('/')[-1]
        cats = [cls.replace('category-', '') for cls in card.get('class', []) if cls.startswith('category-')]
        cat_el = card.find(class_='post-cat')
        primary_cat = cat_el.get_text(strip=True) if cat_el else (cats[0].title() if cats else 'Action')
        genres = ', '.join(cats)
        c.execute('UPDATE games SET category = ?, genres = ? WHERE slug = ?', (primary_cat, genres, slug))
    conn.commit()
    print('Updated categories from steamrip_home.html')
except Exception as e:
    print('Error with steamrip_home.html:', e)

# 2. For games still missing category, detect from title, slug, description
c.execute('SELECT id, title, slug, description FROM games WHERE category IS NULL OR category = ""')
rows = c.fetchall()

def detect(title, slug, desc):
    text = (str(title) + ' ' + str(slug) + ' ' + str(desc or '')).lower()
    cats = []
    if any(k in text for k in ['vr', 'virtual reality']):
        cats.append('vr')
    if any(k in text for k in ['horror', 'survival', 'somnia', 'hellraiser', 'scary', 'spooky', 'fear']):
        cats.append('horror')
    if any(k in text for k in ['anime', 'slayer', 'yaiba', 'naruto', 'dragon ball', 'manga']):
        cats.append('anime')
    if any(k in text for k in ['racing', 'forza', 'drift', 'car', 'speed', 'rally']):
        cats.append('racing')
    if any(k in text for k in ['rpg', 'witcher', 'elden', 'eternia', 'role-playing', 'dungeon']):
        cats.append('rpg')
    if any(k in text for k in ['multiplayer', 'co-op', 'friends', 'online', 'pvp']):
        cats.append('multiplayer')
    if any(k in text for k in ['simulator', 'simulation', 'cafe', 'bakery', 'farm']):
        cats.append('simulation')
    if any(k in text for k in ['strategy', 'tactics', 'war', 'civilization', 'command']):
        cats.append('strategy')
    if any(k in text for k in ['sports', 'fifa', 'nba', 'football', 'soccer']):
        cats.append('sports')
    if any(k in text for k in ['shooter', 'fps', 'sniper', 'gun', 'shooting']):
        cats.append('fps')
    if any(k in text for k in ['open world', 'sandbox']):
        cats.append('open-world')
    if any(k in text for k in ['building', 'craft', 'builder']):
        cats.append('building')
    if any(k in text for k in ['adventure', 'journey', 'quest']):
        cats.append('adventure')
    if any(k in text for k in ['indie']):
        cats.append('indie')
    if not cats:
        cats.append('action')
    
    primary = cats[0].title()
    if primary == 'Fps':
        primary = 'First-person Shooter'
    elif primary == 'Vr':
        primary = 'Virtual Reality'
    elif primary == 'Rpg':
        primary = 'Role-playing Game'
    elif primary == 'Open-World':
        primary = 'Open World'
    return primary, ', '.join(cats)

for gid, title, slug, desc in rows:
    p_cat, g_list = detect(title, slug, desc)
    c.execute('UPDATE games SET category = ?, genres = ? WHERE id = ?', (p_cat, g_list, gid))

conn.commit()

c.execute('SELECT category, count(*) FROM games GROUP BY category ORDER BY count(*) DESC')
for cat, count in c.fetchall():
    print(f'  {cat}: {count} games')

conn.close()
