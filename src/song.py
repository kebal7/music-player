class Song:
    def __init__(self, title, artist, filepath):
        self.title = title
        self.artist = artist
        self.filepath = filepath
        self.upvotes = 0  # For party mode
