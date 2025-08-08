from traffic.NotesClient import NotesClient


notes = NotesClient("test@test.com", "Test")
print("Alle Notes:", notes.list_all())
print("Neue Note:", notes.post("Einkauf", "Milch & Brot", "Grocery"))