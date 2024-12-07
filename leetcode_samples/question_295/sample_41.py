import math 

def findLocation(numList, num) -> int:
    ind = math.floor(len(numList)/2)
    # print(f"in binary serch {numList} for {num} with {ind}")
    if num <= numList[0]:
        return 0
    elif num >= numList[-1]:
        return len(numList)
    elif num <= numList[ind]:
        return findLocation(numList[:ind], num)
    elif num > numList[ind]:
        return ind + 1 + findLocation(numList[(ind+1):], num)


class MedianFinder:

    def __init__(self):
        self.data = []
    def addNum(self, num: int) -> None:
        if not self.data:
            self.data = [num]
        else:
            pos = findLocation(self.data, num)
            self.data.insert(pos, num)
        # print(self.data)
    def findMedian(self) -> float:
        ind = math.floor(len(self.data)/2)
        if len(self.data) % 2 == 1:
            return(self.data[ind])
        else:
            return (self.data[ind-1] + self.data[ind])/2        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()