import requests

def url_funciona(url: str) -> bool:
    """Devuelve True si la URL existe y responde (<400)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        if r.status_code < 400:
            return True
        # Algunos servidores no soportan HEAD
        r = requests.get(url, headers=headers, timeout=5, allow_redirects=True, stream=True)
        return r.status_code < 400
    except requests.RequestException:
        return False
