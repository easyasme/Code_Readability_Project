class MedianFinder:

    def __init__(self):
        self.arr=[]
        

    def addNum(self, num: int) -> None:
        start=0
        end=len(self.arr)
        while start<end:
            mid=(start+end)//2
            if self.arr[mid]>num:
                end=mid
            else:
                start=mid+1
        self.arr.insert(start,num)

    def findMedian(self) -> float:
        mid=len(self.arr)
        if mid%2==1:
            # print(self.min_heap[mid],self.min_heap[mid+1])
            return self.arr[mid//2]
        else:            
            return (self.arr[mid//2-1]+self.arr[mid//2])/2

            
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()