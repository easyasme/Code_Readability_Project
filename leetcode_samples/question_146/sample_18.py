from sortedcontainers import SortedList

class DLL:
    def __init__(self,key,val):
        self.key=key
        self.val=val
        self.next=None
        self.prev=None
    def __lt__(self, other): return True

class LRUCache:

    def __init__(self, capacity: int):
        self.srt=SortedList()
        self.time=0
        self.map={}
        self.time_map={}
        self.cap=capacity
        

    def get(self, key: int) -> int:
        if key not in self.map: return -1
        node=self.map[key]
        t=self.time_map[key]
        self.srt.remove((t,node))
        self.srt.add((self.time,node))
        self.time_map[key]=self.time
        self.time+=1
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            node=self.map[key]
            node.val=value
            self.get(key)
            return
        node=DLL(key,value)
        self.map[key]=node
        self.time_map[key]=self.time
        self.srt.add((self.time,node))
        self.time+=1

        if len(self.srt)>self.cap:
            _,node=self.srt.pop(0)
            del self.map[node.key]
            del self.time_map[node.key]
        
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)