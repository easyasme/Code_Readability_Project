class MedianFinder:

    def __init__(self):
        # Heap for left side of sorted array with smaller numbers.
        # When if becomse bigger by 2 than the right side of array, we need to take the larget elevement
        # and move it to the right side. That's why it is MAX heap.
        self._left_max = []
        self._right_min = []

    def _left_add(self, num: int):
        self._left_max.append(num)
        i = len(self._left_max) - 1
        while i > 0:
            p = (i - 1) // 2
            if self._left_max[i] > self._left_max[p]:
                self._left_max[i], self._left_max[p] = self._left_max[p], self._left_max[i]
                i = p
            else:
                break

    def _left_pop(self) -> int:
        res = self._left_max[0]
        self._left_max[0] = self._left_max[-1]
        # This could be more optimal by memorizing number of active elements in heap.
        self._left_max = self._left_max[:-1]
        i = 0
        while True:
            c = i
            if i * 2 + 1 < len(self._left_max) and self._left_max[i * 2 + 1] > self._left_max[c]:
                c = i * 2 + 1
            if i * 2 + 2 < len(self._left_max) and self._left_max[i * 2 + 2] > self._left_max[c]:
                c = i * 2 + 2
            if c != i:
                self._left_max[i], self._left_max[c] = self._left_max[c], self._left_max[i]
                i = c
            else:
                break
        return res

    def _right_add(self, num: int):
        self._right_min.append(num)
        i = len(self._right_min) - 1
        while i > 0:
            p = (i - 1) // 2
            if self._right_min[i] < self._right_min[p]:
                self._right_min[i], self._right_min[p] = self._right_min[p], self._right_min[i]
                i = p
            else:
                break

    def _right_pop(self) -> int:
        res = self._right_min[0]
        self._right_min[0] = self._right_min[-1]
        # This could be more optimal by memorizing number of active elements in heap.
        self._right_min = self._right_min[:-1]
        i = 0
        while True:
            c = i
            if i * 2 + 1 < len(self._right_min) and self._right_min[i * 2 + 1] < self._right_min[c]:
                c = i * 2 + 1
            if i * 2 + 2 < len(self._right_min) and self._right_min[i * 2 + 2] < self._right_min[c]:
                c = i * 2 + 2
            if c != i:
                self._right_min[i], self._right_min[c] = self._right_min[c], self._right_min[i]
                i = c
            else:
                break
        return res

    def addNum(self, num: int) -> None:
        l = self._left_max[0] if len(self._left_max) > 0 else None
        r = self._right_min[0] if len(self._right_min) > 0 else None

        if l is None and r is None:
            # Add to any.
            self._left_add(num)
        elif l is not None and r is None:
            if num < l:
                self._left_add(num)
            else:
                self._right_add(num)
        elif l is None and r is not None:
            if num > r:
                self._right_add(num)
            else:
                self._left_add(num)
        else:
            if num <= l:
                self._left_add(num)
            else:
                self._right_add(num)

        while len(self._left_max) + 1 < len(self._right_min):
            self._left_add(self._right_pop())
        while len(self._right_min) + 1 < len(self._left_max):
            self._right_add(self._left_pop())

    def findMedian(self) -> float:
        if len(self._left_max) == len(self._right_min):
            return (self._left_max[0] + self._right_min[0]) * 0.5
        elif len(self._left_max) < len(self._right_min):
            return self._right_min[0]
        else:
            return self._left_max[0]


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()