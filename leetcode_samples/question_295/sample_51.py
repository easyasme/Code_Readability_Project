class MedianFinder:

    def __init__(self):
        self.min_heap = []
        self.max_heap = []

    def bubbleUp(self, arr, sign):
        ind = len(arr) - 1
        while ind != 0 and (arr[ind] - arr[(ind + 1) // 2 - 1]) * sign > 0:
            arr[ind], arr[(ind + 1) // 2 - 1] = arr[(ind + 1) // 2 - 1], arr[ind]
            ind = (ind + 1) // 2 - 1
    
    def bubbleDown(self, arr, sign):
        ind = 0
        while ind + 1 <= len(arr) // 2:
            right = (ind + 1) * 2
            left = (ind + 1) * 2 - 1
            if right >= len(arr) or (arr[left] - arr[right]) * sign > 0:
                swapIndex = left
            else:
                swapIndex = right
            if (arr[ind] - arr[swapIndex]) * sign < 0:
                arr[ind], arr[swapIndex] = arr[swapIndex], arr[ind]
                ind = swapIndex
            else:
                break

    def addNum(self, num: int) -> None:
        if len(self.min_heap) == 0 and len(self.max_heap) == 0:
            self.min_heap.append(num)
        elif len(self.max_heap) == 0:
            self.max_heap.append(num)
            if self.min_heap[0] < self.max_heap[0]:
                self.max_heap[0], self.min_heap[0] = self.min_heap[0], self.max_heap[0]
        else:
            if num < self.max_heap[0]:
                self.max_heap.append(num)
                self.bubbleUp(self.max_heap, 1)
            else:
                self.min_heap.append(num)
                self.bubbleUp(self.min_heap, -1)
            if len(self.min_heap) - len(self.max_heap) > 1:
                self.min_heap[0], self.min_heap[-1] = self.min_heap[-1], self.min_heap[0]
                self.max_heap.append(self.min_heap[-1])
                self.min_heap = self.min_heap[:-1]
                self.bubbleUp(self.max_heap, 1)
                self.bubbleDown(self.min_heap, -1)
            elif len(self.max_heap) - len(self.min_heap) > 1:
                self.max_heap[0], self.max_heap[-1] = self.max_heap[-1], self.max_heap[0]
                self.min_heap.append(self.max_heap[-1])
                self.max_heap = self.max_heap[:-1]
                self.bubbleUp(self.min_heap, -1)
                self.bubbleDown(self.max_heap, 1)

    def findMedian(self) -> float:
        if len(self.min_heap) > len(self.max_heap):
            return self.min_heap[0]
        elif len(self.max_heap) > len(self.min_heap):
            return self.max_heap[0]
        else:
            return (self.min_heap[0] + self.max_heap[0]) / 2


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()