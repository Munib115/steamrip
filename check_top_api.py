import requests

r = requests.get('http://127.0.0.1:8000/games?sort=top&page_size=24').json()
print('Total games in top list:', r['total'])
print('\nFirst 20 Top Games on Website:')
for i, g in enumerate(r['items'][:20]):
    print(f"  #{i+1:2d}: [{g['id']}] {g['title'][:45]} | Rank: {g.get('top_rank')} | Poster: {g.get('thumbnail_url')}")
