class MedianFinder:

    def __init__(self):
        self.left = []
        self.right = []

    def add_left(self, num):
        curr = len(self.left)
        self.left.append(num)
        while curr > 0:
            par = (curr - 1) // 2
            if self.left[curr] > self.left[par]:
                self.left[curr], self.left[par] = self.left[par], self.left[curr]
                curr = par
            else:
                break
    
    def pop_left(self):
        self.left[0], self.left[len(self.left) - 1] = self.left[len(self.left) - 1], self.left[0]
        curr = 0
        while 2 * curr + 1 < len(self.left) - 1:
            l_par = 2 * curr + 1
            r_par = 2 * curr + 2
            if r_par < len(self.left) - 1 and self.left[r_par] > self.left[l_par] and self.left[r_par] > self.left[curr]:
                self.left[r_par], self.left[curr] = self.left[curr], self.left[r_par]
                curr = r_par
            elif self.left[l_par] > self.left[curr]:
                self.left[l_par], self.left[curr] = self.left[curr], self.left[l_par]
                curr = l_par
            else:
                break
        return self.left.pop()

    def add_right(self, num):
        curr = len(self.right)
        self.right.append(num)
        while curr > 0:
            par = (curr - 1) // 2
            if self.right[curr] < self.right[par]:
                self.right[curr], self.right[par] = self.right[par], self.right[curr]
                curr = par
            else:
                break

    def pop_right(self):
        self.right[0], self.right[len(self.right) - 1] = self.right[len(self.right) - 1], self.right[0]
        curr = 0
        while 2 * curr + 1 < len(self.right) - 1:
            l_par = 2 * curr + 1
            r_par = 2 * curr + 2
            if r_par < len(self.right) - 1 and self.right[r_par] < self.right[l_par] and self.right[r_par] < self.right[curr]:
                self.right[r_par], self.right[curr] = self.right[curr], self.right[r_par]
                curr = r_par
            elif self.right[l_par] < self.right[curr]:
                self.right[l_par], self.right[curr] = self.right[curr], self.right[l_par]
                curr = l_par
            else:
                break
        return self.right.pop()
                
    def addNum(self, num: int) -> None:
        if len(self.right) == len(self.left) == 0:
            self.add_right(num)
        elif len(self.right) <= len(self.left):
            if num >= self.left[0]:
                self.add_right(num)
            else:
                self.add_right(self.pop_left())
                self.add_left(num)
        else:
            if num <= self.right[0]:
                self.add_left(num)
            else:
                self.add_left(self.pop_right())
                self.add_right(num)

    def findMedian(self) -> float:
        if len(self.left) == len(self.right):
            return (self.left[0] + self.right[0]) / 2
        else:
            return self.right[0]
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()