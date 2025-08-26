import os

class Node:
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None

class Playlist:
    def __init__(self, music_dir):
        # Create nodes for each song
        songs = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.endswith(".mp3")]
        self.head = None
        self.current_node = None

        if not songs:
            raise ValueError("No mp3 files found in the directory.")

        prev_node = None
        for s in songs:
            node = Node(s)
            if self.head is None:
                self.head = node
            if prev_node:
                prev_node.next = node
                node.prev = prev_node
            prev_node = node

        # Make circular
        self.head.prev = prev_node
        prev_node.next = self.head

        # Start at head
        self.current_node = self.head

    def current(self):
        return self.current_node.song

    def next(self):
        self.current_node = self.current_node.next
        return self.current_node.song

    def previous(self):
        self.current_node = self.current_node.prev
        return self.current_node.song

    def get_index(self):
        """Optional: get index in the original list if needed"""
        idx = 0
        node = self.head
        while node != self.current_node:
            node = node.next
            idx += 1
        return idx

    def go_to_index(self, index):
        """Go to a specific song index (0-based)"""
        node = self.head
        for _ in range(index):
            node = node.next
        self.current_node = node
        return self.current_node.song

