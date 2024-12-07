class MedianFinder:

    def __init__(self):
        self.list = []

    def addNum(self, num):
        if len(self.list) == 0:
            self.list.append(num)
        elif num < self.list[0]:
            self.list.insert(0,num)
        elif num > self.list[-1]:
            self.list.append(num)
        else:
            self.list.append(num)
            self.list.sort()

    def findMedian(self) -> float:
        center = len(self.list) // 2
        if len(self.list) % 2 == 1:
            return self.list[center]
        else:
            return (self.list[center - 1] + self.list[center])/2