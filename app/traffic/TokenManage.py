import time, requests
from jose import jwt

from key import PUBLIC_KEY

#TODO
REGISTER_URL = "http://localhost:8000/auth/register"
LOGIN_URL = "http://localhost:8000/auth/login"
KEY_URL = "http://localhost:8000/auth/public_key"
ACCESS_TOKEN_LIFETIME = 30 * 60

class TokenManager:
    """_summary_
    Classe zur Clientseitigen Token Validierung und Verifizierung mit der API.
    Authentifiezierung geschieht über email und password.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.expiers_at = 0
        self.public_key = None
    
    def authenticate(self):
        resp = requests.post(
            LOGIN_URL,
            data={
                "username": self.username, 
                "password": self.password})
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access_token"]
        self.expires_at = time.time() + ACCESS_TOKEN_LIFETIME
    
    def register(self, name: str):
        print(name, self.username, self.password)
        resp = requests.post(
            REGISTER_URL,
            json={
                "name": name, 
                "email": self.username, 
                "password": self.password})
        resp.raise_for_status()
        return resp.json()
    
    def get_token(self):
        if not self.token or time.time() > self.expiers_at - 60:
            self.authenticate()
        return self.token
    
    def _load_public_key(self):
        if not self.public_key:
            resp = requests.get(KEY_URL)
            resp.raise_for_status()
            self.public_key = resp.text
        return self.public_key
    
    def verify(self, token):
        return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])