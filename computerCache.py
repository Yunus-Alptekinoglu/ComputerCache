

class Node:


    def __init__(self, content):
        self.value = content
        self.next = None
        self.previous = None


    def __str__(self):
        return ('CONTENT:{}\n'.format(self.value))


    __repr__=__str__


class ContentItem:


    def __init__(self, cid, size, header, content):
        self.cid = cid
        self.size = size
        self.header = header
        self.content = content


    def __str__(self):
        return f'CONTENT ID: {self.cid} SIZE: {self.size} HEADER: {self.header} CONTENT: {self.content}'


    __repr__=__str__


    def __eq__(self, other):
        if isinstance(other, ContentItem):
            return self.cid == other.cid and self.size == other.size and self.header == other.header and self.content == other.content
        return False


    # Returns the hash value of a ContentItem
    def __hash__(self):
        total = 0
        for char in self.header:
            total += ord(char)
        total = int(total % 3)
        return total


class CacheList:


    def __init__(self, size):
        self.head = None
        self.tail = None
        self.maxSize = size
        self.remainingSpace = size
        self.numItems = 0


    def __str__(self):
        listString = ""
        current = self.head
        while current is not None:
            listString += "[" + str(current.value) + "]\n"
            current = current.next
        return 'REMAINING SPACE:{}\nITEMS:{}\nLIST:\n{}'.format(self.remainingSpace, self.numItems, listString)  


    __repr__=__str__


    def __len__(self):
        return self.numItems


    def put(self, content, evictionPolicy):
        # Check if content.size is greater than self.maxSize and content.cid is in self
        if content.size > self.maxSize:
            return 'Insertion not allowed'
        if content.cid in self:
            return f'Content {content.cid} already in cache, insertion not allowed'
        # Evict according to the eviction policy until there is enough space to add content
        while content.size > self.remainingSpace:
            if evictionPolicy == 'mru':
                self.mruEvict()
            elif evictionPolicy == 'lru':
                self.lruEvict()
        # Create a new node and make it the head node
        newNode = Node(content)
        if not self.head:
            self.head = newNode
            self.tail = newNode
            self.numItems += 1
            self.remainingSpace -= content.size
        else:
            self.head.previous = newNode
            newNode.next = self.head
            self.head = newNode
            self.numItems += 1
            self.remainingSpace -= content.size
        return f'INSERTED: {content}'


    def __contains__(self, cid):
        # Check if the head node exists, the head node contains cid, or the tail node contains cid
        if not self.head:
            return False
        if self.head.value.cid == cid:
            return True
        if self.tail.value.cid == cid:
            self.tail.previous.next = None
            self.head.previous = self.tail
            self.tail.next = self.head
            self.head = self.tail
            self.tail = self.tail.previous
            return True
        current = self.head
        # Remove the node containing cid and make it the head node
        while current.next:
            if current.value.cid == cid:
                current.previous.next = current.next
                current.next.previous = current.previous
                self.head.previous = current
                current.next = self.head
                self.head = current
                self.head.previous = None
                return True
            current = current.next
        return False


    # If cid is in self and there is enough space, updates its value to content
    def update(self, cid, content):
        if cid in self:
            space = self.remainingSpace + self.head.value.size
            space -= content.size
            if space < 0:
                return 'Cache miss!'
            self.head.value = content
            self.remainingSpace = space
            return f'UPDATED: {self.head.value}'
        return 'Chache miss!'
        

    # Removes the head node
    def mruEvict(self):
        if len(self) == 1:
            current = self.head
            self.head = None
            self.tail = None
            self.numItems -= 1
            self.remainingSpace += current.value.size
        elif len(self) > 1:
            current = self.head
            self.head.next.previous = None
            self.head = self.head.next.next.previous
            self.head.previous = None
            self.numItems -= 1
            self.remainingSpace += current.value.size
        

    # Removes the tail node
    def lruEvict(self):
        if len(self) == 1:
            current = self.tail
            self.tail = None
            self.head = None
            self.numItems -= 1
            self.remainingSpace += current.value.size
        elif len(self) > 1:
            current = self.tail
            self.tail.previous.next = None
            self.tail = self.tail.previous
            self.numItems -= 1
            self.remainingSpace += current.value.size
        

    # Clears the cache
    def clear(self):
        self.head = None
        self.tail = None
        self.remainingSpace = self.maxSize
        self.numItems = 0
        return 'Cleared cache!'
        

class Cache:


    def __init__(self):
        self.hierarchy = [CacheList(200), CacheList(200), CacheList(200)]
        self.size = 3
    

    def __str__(self):
        return ('L1 CACHE:\n{}\nL2 CACHE:\n{}\nL3 CACHE:\n{}\n'.format(self.hierarchy[0], self.hierarchy[1], self.hierarchy[2]))
    

    __repr__=__str__


    def clear(self):
        for item in self.hierarchy:
            item.clear()
        return 'Cache cleared!'

    
    # Inserts a ContentItem into the corresponding CacheList
    def insert(self, content, evictionPolicy):
        return self.hierarchy[hash(content)].put(content, evictionPolicy)


    # Returns a reference to a node that stores a ContentItem
    def __getitem__(self, content):
        if hash(content) in self.hierarchy:
            return self.hierarchy[hash(content)]
        return 'Cache miss!'
        

    # Updates a ContentItem
    def updateContent(self, content):
        return self.hierarchy[hash(content)].update(content.cid, content)
    
