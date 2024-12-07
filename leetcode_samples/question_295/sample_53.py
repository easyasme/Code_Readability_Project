class Heap:
    def __init__(self, isMax):
        self.heap = []
        self.isMax = isMax
    def getParent(self, index):
        if index%2==0:
            return index//2-1
        else:
            return index//2
    def heapify(self, index, n=None, arr=None):
        if arr is None:
            arr = self.heap
            n = len(arr)
        lowest=index
        left = index*2 + 1
        right = left + 1
        if left<n and arr[left]<arr[lowest]:
            lowest = left
        if right<n and arr[right]<arr[lowest]:
            lowest = right
        if lowest!=index:
            arr[index], arr[lowest] = arr[lowest], arr[index]
            self.heapify(lowest, n, arr)
    def push(self, val):
        if self.isMax==1:
            val*=-1
        self.heap.append(val)
        index = len(self.heap)-1
        parent = self.getParent(index)
        while parent>=0 and self.heap[index]<self.heap[parent]:
            self.heap[parent], self.heap[index] = self.heap[index], self.heap[parent]
            index = parent
            parent = self.getParent(index)
    def top(self):
        if self.isMax==1:
            return self.heap[0] * -1
        return self.heap[0]
    def pop(self):
        top = self.heap[0]
        if self.isMax==1:
            top*=-1
        self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
        self.heap = self.heap[:-1]
        self.heapify(0)
        return top
class MedianFinder:

    def __init__(self):
        self.right = Heap(0)
        self.left = Heap(1)

    def balanceHeaps(self):
        if len(self.right.heap)-len(self.left.heap)>1:
            self.left.push(self.right.pop())
        elif len(self.left.heap)-len(self.right.heap)>1:
            self.right.push(self.left.pop())
        else:
            return

    def addNum(self, num: int) -> None:
        if len(self.right.heap)==0 or num>self.right.top():
            self.right.push(num)
        else:
            self.left.push(num)
        self.balanceHeaps()

    def findMedian(self) -> float:
        if len(self.right.heap)==len(self.left.heap):
            return (self.right.top() + self.left.top()) / 2
        elif len(self.right.heap)>len(self.left.heap):
            return self.right.top()
        else:
            return self.left.top()


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()