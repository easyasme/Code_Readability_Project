import bisect

class MedianFinder:

    def __init__(self):
        self.med = 0.0
        self.vals = []
        self.size = 0

    def addNum(self, num: int) -> None:
        if self.size == 0:
            self.vals.append(num)
            self.med = float(num)
            self.size += 1
        else:
            bisect.insort(self.vals, num)
            self.size += 1
            if self.size % 2 == 1:
                self.med = self.vals[self.size // 2]
            else:
                medL = self.vals[(self.size // 2) - 1]
                medR = self.vals[self.size // 2]
                print(medL)
                print(medR)
                self.med = (medL + medR) / 2
            

    def findMedian(self) -> float:
        return float(self.med)