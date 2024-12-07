import heapq
class MedianFinder:

    def __init__(self):
        self.min_heap = []
        self.max_heap = []

    def addNum(self, num: int) -> None:
        heapq.heappush(self.min_heap, num)
        heapq.heappush(self.max_heap, -heapq.heappop(self.min_heap))
        while ((len(self.max_heap)-len(self.min_heap))>1):
            heapq.heappush(self.min_heap, -heapq.heappop(self.max_heap))
        #print("A:", self.max_heap, self.min_heap)
        """while (len(self.min_heap) and len(self.max_heap) and self.min_heap[0]<-self.max_heap[0]):
            temp1=heapq.heappop(self.min_heap)
            temp2=heapq.heappop(self.max_heap)
            heapq.heappush(self.min_heap,-temp2)
            heapq.heappush(self.max_heap,-temp1)"""
        #print("B:",self.max_heap, self.min_heap)
        

    def findMedian(self) -> float:
        if(len(self.min_heap)==len(self.max_heap)):
            return (self.min_heap[0]-self.max_heap[0])/2
        else:
            return -self.max_heap[0]
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()Saeascasfbajavavegaff
# obj.addNum(num)
# param_2 = obj.findMedian()