import requests

for q in ['tom clancy', 'tom clancys', "tom clancy's", 'rainbow six', 'splinter cell', 'ghost recon', 'the division', 'racing']:
    r = requests.get('http://127.0.0.1:8000/games', params={'search': q}).json()
    total = r.get('total', 0)
    items = [i['title'][:35] for i in r.get('items', [])[:3]]
    print(f"Search '{q}' -> {total} matches: {items}")
