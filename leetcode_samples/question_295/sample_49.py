class MedianFinder:
    # I just need a sorted list, and then track the length to go to the median/ med avg
    def __init__(self):
        #print("hi")
        self.data=[]
        self.size=0
        #for x in range (0,20):
        #    print(int( (x-1)/2),[0]*x)

    def addNum(self, num: int) -> None:
        self.binaryAdd(num)

    def findMedian(self) -> float:
        
        med =int( (self.size-1)/2)
        #print(med,self.size)
        if self.size%2==0:
            #print("here",(self.data[med]+self.data[med-1])/2)
            return (self.data[med]+self.data[med+1])/2
        else:
            #print("odd return",self.data[med])
            return self.data[med]
    def binaryAdd(self,num:int) -> None:
        #print(num)
        if len(self.data)>0 and num > self.data[len(self.data)-1]:
            self.data.append(num)
        elif len(self.data)>0 and num<self.data[0]:
            self.data.insert(0,num)
        else:
            self.data.append(num)
            self.data.sort()
        self.size+=1
        #print(self.data)
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()