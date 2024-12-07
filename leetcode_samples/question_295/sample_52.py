class MedianFinder:

    def __init__(self):
        self.streamArr = []

    def addNum(self, num: int) -> None:
        if self.streamArr and num <= self.streamArr[0]:
            self.streamArr.insert(0,num)
        elif not self.streamArr or num >= self.streamArr[-1]:
            self.streamArr.append(num)
        else:
            idx = 0
            low = 0
            high = len(self.streamArr)
            if num >= self.streamArr[len(self.streamArr) // 2]:
                low = len(self.streamArr) // 2
            else:
                high = len(self.streamArr) // 2
            for i in range(low,high+1):
                if self.streamArr[i] >= num:
                    idx = i
                    break
            self.streamArr.insert(idx, num)

    def findMedian(self) -> float:
        ls = len(self.streamArr)
        if ls % 2 == 0:
            return (self.streamArr[ls // 2 - 1] + self.streamArr[(ls // 2)]) / 2
        else:
            return self.streamArr[ls // 2]

# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()