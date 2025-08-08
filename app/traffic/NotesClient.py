import requests

class NotesClient:
    def __init__(self, token: str):
        # Das ist der ctor: hier initialisieren wir das Objekt
        self.token = token
        self.base_url = "http://localhost:8000/users/notes"

    def _auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def list_all(self):
        resp = requests.get(self.base_url, headers=self._auth_header())
        resp.raise_for_status()
        return resp.json()

    def post(self, title: str, text: str, category: int):
        resp = requests.post(
            f"{self.base_url}/post",
            json={"title": title, "text": text, "category": category},
            headers=self._auth_header()
        )
        resp.raise_for_status()
        return resp.json()