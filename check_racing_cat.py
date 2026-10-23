import requests

r = requests.get('http://127.0.0.1:8000/games?category=racing&page_size=10').json()
print('Total in racing category:', r.get('total'))
print('First 8 items:')
for g in r.get('items', [])[:8]:
    print(f"  [{g['id']}] {g['title'][:45]} | Cat: {g.get('category')} | Genres: {g.get('genres')}")
