class MedianFinder:
    def __init__(self):
        def smaller(val1, val2):
            if val1 < val2:
                return True
            return False

        def greater(val1, val2):
            if val1 > val2:
                return True
            return False

        class heap:
            def __init__(self, minheap=False):
                self.list = []
                self.maxindex = -1
                self.compare = greater
                if minheap:
                    self.compare = smaller

            def push(self, num):
                self.list.append(num)
                self.maxindex += 1
                self.float(self.maxindex)

            def pop(self):
                if self.maxindex == -1:
                    return None
                item = self.list[0]
                self.list[0] = self.list[-1]
                del self.list[-1]
                self.maxindex -= 1
                if self.maxindex > 0:
                    self.sink(0)
                return item

            def sink(self, index):
                left = 2 * index + 1
                right = 2 * index + 2
                mindex = index
                if left <= self.maxindex and self.compare(
                    self.list[left], self.list[mindex]
                ):
                    mindex = left
                if right <= self.maxindex and self.compare(
                    self.list[right], self.list[mindex]
                ):
                    mindex = right
                if mindex != index:
                    self.list[mindex], self.list[index] = (
                        self.list[index],
                        self.list[mindex],
                    )
                    self.sink(mindex)

            def float(self, index):
                if index == 0:
                    return
                parent = (index - 1) // 2
                if self.compare(self.list[index], self.list[parent]):
                    self.list[index], self.list[parent] = (
                        self.list[parent],
                        self.list[index],
                    )
                    self.float(parent)

        self.left = heap()
        self.val = None
        self.right = heap(True)
        self.empty = True

    def addNum(self, num: int) -> None:
        if self.empty:
            if self.val == None:
                self.val = num
            else:
                if self.val < num:
                    self.left.push(self.val)
                    self.right.push(num)
                else:
                    self.left.push(num)
                    self.right.push(self.val)
                self.empty = False
                self.val = None
        else:
            if self.val == None:
                if num < self.left.list[0]:
                    self.val = self.left.pop()
                    self.left.push(num)
                elif num > self.right.list[0]:
                    self.val = self.right.pop()
                    self.right.push(num)
                else:
                    self.val = num
            else:
                if self.val < num:
                    self.left.push(self.val)
                    self.right.push(num)
                else:
                    self.left.push(num)
                    self.right.push(self.val)
                self.val = None

    def findMedian(self) -> float:
        if self.val == None:
            return (self.left.list[0] + self.right.list[0]) / 2
        return self.val


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()
