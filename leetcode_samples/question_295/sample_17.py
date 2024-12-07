def heapUp(heap, p, isUpper):
    if p == 0:
        return
    q = (p - 1)//2
    if (isUpper and heap[q] > heap[p]) or (not isUpper and heap[q] < heap[p]):
        temp = heap[p]
        heap[p] = heap[q]
        heap[q] = temp
        heapUp(heap, q, isUpper)
def heapDown(heap, p, isUpper):
    nextP = p
    q = p* 2 + 1
    if q < len(heap) and ((isUpper and heap[q] < heap[nextP]) or (not isUpper and heap[q] > heap[nextP])):
        nextP = q
    q = p* 2 + 2
    if q < len(heap) and ((isUpper and heap[q] < heap[nextP]) or (not isUpper and heap[q] > heap[nextP])):
        nextP = q
    if nextP != p:
        temp = heap[p]
        heap[p] = heap[nextP]
        heap[nextP] = temp
        heapDown(heap, nextP, isUpper)
def pushHeap(heap, n, isUpper):
    heap.append(n)
    heapUp(heap, len(heap) - 1, isUpper)
def popHeap(heap, isUpper):
    result = heap[0]
    heap[0] = heap[len(heap) - 1]
    heap.pop()
    if len(heap) == 0:
        return
    heapDown(heap, 0, isUpper)
    return result

class MedianFinder:
    def __init__(self):
        self.upperHeap = []
        self.lowerHeap = []
        self.firstNumber = None

    def addNum(self, num: int) -> None:
        if self.firstNumber == None:
            self.firstNumber = num
        elif len(self.upperHeap) == 0:
            pushHeap(self.upperHeap, max(num, self.firstNumber), True)
            pushHeap(self.lowerHeap, min(num, self.firstNumber), False)
        else:
            if len(self.upperHeap) > len(self.lowerHeap) and num < self.upperHeap[0]:
                pushHeap(self.lowerHeap, num, False)
            elif len(self.upperHeap) == len(self.lowerHeap) and num > self.lowerHeap[0]:
                pushHeap(self.upperHeap, num,  True)
            elif len(self.upperHeap) > len(self.lowerHeap):
                pushHeap(self.upperHeap, num, True)
                newNum =  popHeap(self.upperHeap, True)
                pushHeap(self.lowerHeap, newNum, False)
            else:
                pushHeap(self.lowerHeap, num, False)
                newNum =  popHeap(self.lowerHeap, False)
                pushHeap(self.upperHeap, newNum, True)
        # print(num, self.upperHeap, self.lowerHeap)

    def findMedian(self) -> float:
        if len(self.upperHeap) == 0:
            return float(self.firstNumber)
        elif len(self.upperHeap) > len(self.lowerHeap):
            return float(self.upperHeap[0])
        else:
            return (self.upperHeap[0] + self.lowerHeap[0]) / 2

# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()