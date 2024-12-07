import heapq
class MedianFinder:

    def __init__(self):
        self.maxheap=[]
        self.minheap=[]
        
    def addNum(self, num: int) -> None:
        if len(self.maxheap)-len(self.minheap)<1:
            heapq.heappush(self.maxheap,-1*num)

        else:
             heapq.heappush(self.minheap,num)

        if len(self.maxheap)>0 and len(self.minheap)>0:
            x=-1*heapq.heappop(self.maxheap)
            y=heapq.heappop(self.minheap)
        
            if x>y:
                heapq.heappush(self.minheap,x)
                heapq.heappush(self.maxheap,-y)
            else:
                heapq.heappush(self.minheap,y)
                heapq.heappush(self.maxheap,-x)
            

    def findMedian(self) -> float:
       l=len(self.maxheap+self.minheap)
       if l%2==0:
        m1=-1*heapq.heappop(self.maxheap)
        m2=heapq.heappop(self.minheap)
        median=(m1+m2)/2
        heapq.heappush(self.maxheap,-1*m1)
        heapq.heappush(self.minheap,m2)
        return median

       else:
        m1=-1*heapq.heappop(self.maxheap)
        heapq.heappush(self.maxheap,-1*m1)
        return m1


             


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()