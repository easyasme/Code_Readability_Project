from sortedcontainers import SortedList

class MedianFinder:
    def __init__(self):
        self.left = SortedList()
        self.right = SortedList()
    
    def _balance(self):
        while len(self.left) < len(self.right):
           right_min = self.right[0]
           self.right.remove(right_min)
           self.left.add(right_min)
        
        while len(self.left) > len(self.right) + 1:
            left_max = self.left[-1]
            self.left.remove(left_max)
            self.right.add(left_max)

    def addNum(self, num: int) -> None:
        if not self.left or num <= self.left[-1]:
            self.left.add(num)
        else:
            self.right.add(num)
        self._balance()
        

    def findMedian(self) -> float:
        if (len(self.left) + len(self.right)) % 2 == 1:
            return self.left[-1]
        
        return .5 * (self.left[-1] + self.right[0])
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()