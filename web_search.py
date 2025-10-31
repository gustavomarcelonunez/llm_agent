from bs4 import BeautifulSoup
import requests

def search_in(url):
    print(url)
    
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/117.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    print("Status code: " . r.status_code)
    if r.status_code != 200:
        return "No se encontró información."
    
    soup = BeautifulSoup(r.text, 'html.parser')
    parrafos = soup.find_all('p')
    
    # Tomamos solo párrafos con texto suficiente
    texto = " ".join([p.get_text().strip() for p in parrafos if len(p.get_text().strip()) > 50][:5])
    
    if not texto:
        return "No se encontró información específica para resumir."
    
    return texto