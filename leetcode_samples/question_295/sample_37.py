class MedianFinder:

    def __init__(self):
        self.B = [[] for _ in range(401)]
        self.ct = [0 for _ in range(401)]
        self.n = 0

    def addNum(self, num: int) -> None:
        num += 10**5
        self.B[num//500].append(num)
        self.ct[num//500] += 1
        self.n += 1
    
    def find(self, idx):
        s = 0

        for i in range(401):
            #print(i, s)
            if s + self.ct[i] < idx:
                s += self.ct[i]
            else:
                self.B[i].sort()
                return self.B[i][idx-s-1]

    def findMedian(self) -> float:
        if self.n % 2:
            return self.find((self.n+1)//2)-10**5
        else:
            #print(self.find(self.n), self.find(self.n+1))
            return (self.find(self.n//2)+self.find(self.n//2+1))/2-10**5


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()