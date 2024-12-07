class MedianFinder:

    def __init__(self):
        self.l=[]
        self.size=0
        

    def addNum(self, num: int) -> None:
        if self.l:
            if num>=self.l[-1]:
                self.l.append(num)
            elif num<=self.l[0]:
                self.l.insert(0,num)
            else:
                self.l.append(num)
                self.l.sort()
        else:
            self.l.append(num)
        self.size+=1

    def findMedian(self) -> float:
        m=(self.size)//2

        if (self.size)%2==0:
            return (self.l[m-1]+self.l[m])/2
        else:
            return self.l[m]