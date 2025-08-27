import random

class Node:
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None

class PlaylistLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, song):
        # Prevent duplicates
        current = self.head
        while current:
            if current.song.filepath == song.filepath:
                return False
            current = current.next
        new_node = Node(song)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1
        return True

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        self.size -= 1

    def to_list(self):
        songs = []
        current = self.head
        while current:
            songs.append(current.song)
            current = current.next
        return songs

    def shuffle(self):
        songs = self.to_list()
        def recursive_shuffle(songs):
            if len(songs) <= 1:
                return songs
            pivot = random.choice(songs)
            remaining = [s for s in songs if s != pivot]
            return [pivot] + recursive_shuffle(remaining)
        shuffled = recursive_shuffle(songs)
        self.head = self.tail = None
        for s in shuffled:
            self.append(s)

