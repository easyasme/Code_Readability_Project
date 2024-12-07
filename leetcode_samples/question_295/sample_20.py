class MedianFinder:



    class Heap:


        def __init__(self, comparison_function, init_array):

            self.arr = init_array
            self.comp = comparison_function
            n = len(self.arr)
            i = n - 1
            while i >= 0:
                self.downheap(i)
                i -= 1



        def insert(self, value):

            # Write your code here
            self.arr.append(value)
            self.upheap(len(self.arr) - 1)

        def extract(self):
            if len(self.arr) == 0:
                return None
            else:
                ans = self.arr[0]
                self.arr[0] = self.arr[-1]
                self.arr.pop(-1)
                if (len(self.arr) != 0):
                    self.downheap(0)
                return ans


        def top(self):
            if (len(self.arr) > 0):
                return self.arr[0]
            else:
                return None

        def upheap(self, i):
            while i>0:
                if(self.comp(self.arr[i],self.arr[(i-1)//2])):
                    self.arr[i],self.arr[(i-1)//2]=self.arr[(i-1)//2],self.arr[i]
                    i=(i-1)//2
                else:
                    break


        def downheap(self, i):
            n = len(self.arr)
            while True:
                smallest=i
                left=2*i+1
                right=2*i+2
                if(left<n and self.comp(self.arr[left],self.arr[smallest])):
                    smallest=left
                if(right<n and self.comp(self.arr[right],self.arr[smallest])):
                    smallest=right
                if(smallest==i):
                    break
                self.arr[smallest],self.arr[i]=self.arr[i],self.arr[smallest]
                i=smallest





    def __init__(self):
        def comp(x,y):
            return x<y
        self.h1=self.Heap(comp,[])
        self.h2=self.Heap(comp,[])
        

    def addNum(self, num: int) -> None:
        if(len(self.h1.arr)==0):
            self.h1.insert(-num)
            return
        if(len(self.h2.arr)==0):
            self.h1.insert(-num)
            temp=-self.h1.extract()
            self.h2.insert(temp)
            return 
        if(len(self.h1.arr)==len(self.h2.arr)):
            if(num>-(self.h1.top())):
                self.h2.insert(num)
                temp=self.h2.extract()
                self.h1.insert(-temp)
            else:
                self.h1.insert(-num)
        else:
            if(num>-(self.h1.top())):
                self.h2.insert(num)
            else:
                self.h1.insert(-num)
                temp=-(self.h1.extract())
                self.h2.insert(temp)



    def findMedian(self) -> float:
        if(len(self.h1.arr)==len(self.h2.arr)):
            return (-(self.h1.top())+self.h2.top())/2
        else:
            return -self.h1.top()
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()