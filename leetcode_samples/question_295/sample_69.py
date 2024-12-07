class MedianFinder:

    def __init__(self):
        self.A=[]
        self.h=[]

    def addNum(self, num: int) -> None:
        # print(num)
        self.A.append(num)
        # self.A.sort()

    def findMedian(self) -> float:
        self.A.sort()
        if(len(self.A)%2==1):
           return self.A[len(self.A)//2]
        else:
           return (self.A[len(self.A)//2]+self.A[len(self.A)//2-1])/2
            


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()