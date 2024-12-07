class MedianFinder:

    def __init__(self):
        self.list = []

    def addNum(self, num: int) -> None:
        if len(self.list) == 0:
            self.list.append(num)
        elif num < self.list[0]:
            self.list.insert(0,num)
        elif num < self.list[-1]:
            self.list.append(num)
            self.list.sort()
        else:
            self.list.append(num)
        

    def findMedian(self) -> float:
        center = len(self.list) // 2
        if len(self.list) % 2 == 1:
            return self.list[center]
        else:
            return sum(self.list[center - 1: center + 1])/2 
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()