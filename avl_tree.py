"""AVL index for workouts ordered by (UTC timestamp, workout ID).

Phase 3 optimizations (same AVL tree, same Big-O, much less work per call):
  1. insert() is a loop instead of recursion, and it STOPS EARLY: walking back
     up, it stops as soon as a node's height is unchanged or one rotation has
     restored the subtree's height, because nothing above can change after that.
     The recursive version recomputed every level on every insert (~15 levels
     at 100k rows), which cProfile showed as 1.5M _insert calls and 6M _height calls.
  2. Heights are read directly (node.left.height if node.left else 0) instead
     of through _height/_fix_height/_balance helper calls.
  3. _Node uses __slots__: smaller nodes, faster attribute access.
  4. range_search() is a loop with an explicit stack that skips subtrees entirely
     before the start date and stops at the first key after the end date.
"""
from typing import Any, Optional


class _Node:
    __slots__ = ("key", "workout", "left", "right", "height")

    def __init__(self, key, workout):
        self.key = key
        self.workout = workout
        self.left: Optional["_Node"] = None
        self.right: Optional["_Node"] = None
        self.height = 1


def _update_height(node):
    lh = node.left.height if node.left else 0
    rh = node.right.height if node.right else 0
    node.height = (lh if lh > rh else rh) + 1


def _rotate_right(y):
    x = y.left
    y.left = x.right
    x.right = y
    _update_height(y)
    _update_height(x)
    return x


def _rotate_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    _update_height(x)
    _update_height(y)
    return y


class AVLTree:
    """AVL tree: O(log n) insertion; O(log n + k) inclusive range queries."""

    def __init__(self):
        self.root: Optional[_Node] = None

    def insert(self, key, workout: Any):
        """Insert a unique key. O(log n). Raises ValueError on a duplicate key."""
        new = _Node(key, workout)
        node = self.root
        if node is None:
            self.root = new
            return
        # 1. Walk DOWN with a loop, remembering the path.
        path = []
        while True:
            path.append(node)
            if key < node.key:
                if node.left is None:
                    node.left = new
                    break
                node = node.left
            elif key > node.key:
                if node.right is None:
                    node.right = new
                    break
                node = node.right
            else:
                raise ValueError('Duplicate date index key')
        # 2. Walk back UP the path, fixing heights, and stop as early as possible.
        for i in range(len(path) - 1, -1, -1):
            node = path[i]
            lh = node.left.height if node.left else 0
            rh = node.right.height if node.right else 0
            balance = lh - rh
            if balance > 1 or balance < -1:
                if balance > 1:                       # left-heavy: LL or LR
                    if key > node.left.key:
                        node.left = _rotate_left(node.left)
                    subtree = _rotate_right(node)
                else:                                 # right-heavy: RR or RL
                    if key < node.right.key:
                        node.right = _rotate_right(node.right)
                    subtree = _rotate_left(node)
                if i == 0:
                    self.root = subtree
                elif path[i - 1].left is node:
                    path[i - 1].left = subtree
                else:
                    path[i - 1].right = subtree
                return          # one rotation restores the old height: ancestors unchanged
            new_height = (lh if lh > rh else rh) + 1
            if new_height == node.height:
                return          # height unchanged: nothing above can change
            node.height = new_height

    def range_search(self, start_utc, end_utc):
        """Return workouts sorted by UTC time then workout ID, inclusive of both bounds.

        Iterative in-order walk: O(log n + k) for k results.
        """
        result = []
        stack = []
        node = self.root
        while True:
            while node is not None:
                if node.key[0] < start_utc:     # node and its left subtree are too early
                    node = node.right
                else:
                    stack.append(node)
                    node = node.left
            if not stack:
                break
            node = stack.pop()
            if node.key[0] > end_utc:           # in-order: everything after is later too
                break
            result.append(node.workout)
            node = node.right
        return result

    def validate_balance(self):
        """Test helper: check BST ordering and AVL height/balance invariants."""
        def check(node, low=None, high=None):
            if not node:
                return 0
            if low is not None and not low < node.key:
                raise AssertionError('BST lower bound broken')
            if high is not None and not node.key < high:
                raise AssertionError('BST upper bound broken')
            left = check(node.left, low, node.key)
            right = check(node.right, node.key, high)
            if abs(left - right) > 1 or node.height != 1 + max(left, right):
                raise AssertionError('AVL balance/height broken')
            return node.height
        check(self.root)
        return True
