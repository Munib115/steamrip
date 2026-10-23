import requests

for gid in [1752, 4860, 4861, 4864, 1168, 8, 4868]:
    r = requests.get(f'http://127.0.0.1:8000/games/{gid}').json()
    files = [(f['label'], f['url'][:45]) for f in r.get('files', [])]
    print(f"Game [{gid}] {r['title'][:35]}: {files}")
