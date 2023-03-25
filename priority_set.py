import heapq

class PrioritySet(object):
    def __init__(self):
        self.heap = []
        self.set = set()

    def add(self, d):
        if type(d) is list:
            [self.add(i) for i in d]
        else:
            if not d in self.set:
                heapq.heappush(self.heap, -d)
                self.set.add(d)

    def pop(self):
        d = heapq.heappop(self.heap)
        d= -d
        self.set.remove(d)
        return d
    
    def empty(self):
        return len(self.heap) == 0
    