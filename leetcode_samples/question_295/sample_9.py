from sortedcontainers import SortedList
class MedianFinder:

    def __init__(self):
        """
        initialize your data structure here.
        """
        self.arr = SortedList()

    def addNum(self, num: int) -> None:
        self.arr.add(num)
        

    def findMedian(self) -> float:
        if len(self.arr) == 1:
            return float(self.arr[0])
        elif len(self.arr) % 2 == 0:
            return sum([self.arr[len(self.arr)//2],self.arr[(len(self.arr)//2)-1]])/2
        else:
            return float(self.arr[len(self.arr)//2])
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()