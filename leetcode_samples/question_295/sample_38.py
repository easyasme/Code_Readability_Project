import queue
class MedianFinder:

    def __init__(self):
        self.minq = queue.PriorityQueue()
        self.maxq = queue.PriorityQueue()

    def addNum(self, num: int) -> None:

        if self.minq.empty():
            self.minq.put(-num)
            return

        k1 = - self.minq.get()
        if self.maxq.empty():
            if k1 <= num:
                self.minq.put(-k1)
                self.maxq.put(num)
                return
            else:
                self.minq.put(-num)
                self.maxq.put(k1)
                return
        
        k2 = self.maxq.get()

        if self.minq.qsize() == self.maxq.qsize():
            if num < k2:
                self.minq.put(-num)
                self.minq.put(-k1)
                self.maxq.put(k2)
            else:
                self.minq.put(-k2)
                self.minq.put(-k1)
                self.maxq.put(num)
        elif self.minq.qsize() > self.maxq.qsize():
            if num < k1:
                self.minq.put(-num)
                self.maxq.put(k1)
                self.maxq.put(k2)
            else:
                self.minq.put(-k1)
                self.maxq.put(k2)
                self.maxq.put(num)
        



    def findMedian(self) -> float:

        if self.minq.qsize() > self.maxq.qsize():
            k = - self.minq.get()
            self.minq.put(-k)
            return k
        else:
            k1 = - self.minq.get()
            self.minq.put(-k1)
            k2 = self.maxq.get()
            self.maxq.put(k2)
            return (k1+k2)/2
        
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()