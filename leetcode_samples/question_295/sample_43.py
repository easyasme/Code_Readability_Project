class TreeNode:
    def __init__(self, val):
        self.val = val           # Node value
        self.left = None         # Left child
        self.right = None        # Right child
        self.height = 1          # Height of the node
        self.size = 1            # Size of the subtree rooted at this node


class MedianFinder:
    def __init__(self):
        self.root = None  # Root of the AVL Tree

    # Helper function to get the height of a node
    def _height(self, node):
        return node.height if node else 0

    # Helper function to get the size of a node
    def _size(self, node):
        return node.size if node else 0

    # Helper function to calculate the balance factor of a node
    def _balance_factor(self, node):
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)

    # Right rotate the subtree rooted at `y`
    def _rotate_right(self, y):
        if not y or not y.left:  # Ensure the left child exists
            return y
        x = y.left
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights and sizes
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        x.height = 1 + max(self._height(x.left), self._height(x.right))

        y.size = 1 + self._size(y.left) + self._size(y.right)
        x.size = 1 + self._size(x.left) + self._size(x.right)

        return x

    # Left rotate the subtree rooted at `x`
    def _rotate_left(self, x):
        if not x or not x.right:  # Ensure the right child exists
            return x
        y = x.right
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights and sizes
        x.height = 1 + max(self._height(x.left), self._height(x.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))

        x.size = 1 + self._size(x.left) + self._size(x.right)
        y.size = 1 + self._size(y.left) + self._size(y.right)

        return y

    # Insert a value into the AVL tree
    def _insert(self, node, val):
        if not node:
            return TreeNode(val)

        if val < node.val:
            node.left = self._insert(node.left, val)
        else:
            node.right = self._insert(node.right, val)

        # Update height and size of the current node
        node.height = 1 + max(self._height(node.left), self._height(node.right))
        node.size = 1 + self._size(node.left) + self._size(node.right)

        # Balance the node if needed
        balance = self._balance_factor(node)

        # Left heavy
        if balance > 1:
            if val < node.left.val:  # Left Left Case
                return self._rotate_right(node)
            else:  # Left Right Case
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)

        # Right heavy
        if balance < -1:
            if val > node.right.val:  # Right Right Case
                return self._rotate_left(node)
            else:  # Right Left Case
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)

        return node

    # Find the k-th smallest element in the tree
    def _find_kth(self, node, k):
        if not node:
            return None

        left_size = self._size(node.left)

        if k <= left_size:
            return self._find_kth(node.left, k)
        elif k == left_size + 1:
            return node.val
        else:
            return self._find_kth(node.right, k - left_size - 1)

    # Public function to add a number to the stream
    def addNum(self, num):
        self.root = self._insert(self.root, num)

    # Public function to find the median
    def findMedian(self):
        if not self.root:
            raise ValueError("No numbers are available to find the median.")

        n = self._size(self.root)
        if n % 2 == 1:
            # Odd size: return the middle element
            return self._find_kth(self.root, n // 2 + 1)
        else:
            # Even size: return the average of the two middle elements
            mid1 = self._find_kth(self.root, n // 2)
            mid2 = self._find_kth(self.root, n // 2 + 1)
            return (mid1 + mid2) / 2