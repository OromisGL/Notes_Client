import requests
from jose import jwt

# 1. Public Key laden
resp = requests.get("http://localhost:8000/auth/public_key")
resp.raise_for_status()
PUBLIC_KEY = resp.text

