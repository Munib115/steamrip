import socket, urllib3.util.connection
urllib3.util.connection.allowed_gai_family = lambda: socket.AF_INET
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'Referer': 'https://steamrip.com/'}
for cat in ['category/action', 'category/rpg', 'category/open-world', 'category/shooters', 'category/adventure', 'category/horror', 'category/simulation', 'category/racing']:
    url = f"https://steamrip.com/{cat}/"
    r = requests.get(url, headers=headers, timeout=6)
    soup = BeautifulSoup(r.text, 'html.parser')
    cards = soup.find_all('li', class_='post-item') or soup.find_all('article')
    print(f"{cat} -> Status {r.status_code}, {len(cards)} games on page 1")
