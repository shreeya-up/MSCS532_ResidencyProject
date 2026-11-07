"""AVL index for workouts ordered by (UTC timestamp, workout ID)."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class _Node:
    key: tuple[datetime, str]
    workout: Any
    left: Optional['_Node'] = None
    right: Optional['_Node'] = None
    height: int = 1


class AVLTree:
    """AVL tree: O(log n) insertion; O(log n + k) inclusive range queries."""

    def __init__(self):
        self.root: Optional[_Node] = None

    @staticmethod
    def _height(node):
        return node.height if node else 0

    @classmethod
    def _fix_height(cls, node):
        node.height = 1 + max(cls._height(node.left), cls._height(node.right))

    @classmethod
    def _balance(cls, node):
        return cls._height(node.left) - cls._height(node.right)

    @classmethod
    def _rotate_right(cls, y):
        x = y.left
        middle = x.right
        x.right = y
        y.left = middle
        cls._fix_height(y)
        cls._fix_height(x)
        return x

    @classmethod
    def _rotate_left(cls, x):
        y = x.right
        middle = y.left
        y.left = x
        x.right = middle
        cls._fix_height(x)
        cls._fix_height(y)
        return y

    @classmethod
    def _insert(cls, node, key, workout):
        if node is None:
            return _Node(key, workout)
        if key < node.key:
            node.left = cls._insert(node.left, key, workout)
        elif key > node.key:
            node.right = cls._insert(node.right, key, workout)
        else:
            raise ValueError('Duplicate date index key')
        cls._fix_height(node)
        balance = cls._balance(node)
        if balance > 1:
            if key > node.left.key:
                node.left = cls._rotate_left(node.left)
            return cls._rotate_right(node)
        if balance < -1:
            if key < node.right.key:
                node.right = cls._rotate_right(node.right)
            return cls._rotate_left(node)
        return node

    def insert(self, key, workout):
        """Insert a unique key into this tree."""
        self.root = self._insert(self.root, key, workout)

    def range_search(self, start_utc, end_utc):
        """Return workouts sorted by UTC time then workout ID, inclusive of boundaries."""
        result = []

        def walk(node):
            if node is None:
                return
            timestamp, _ = node.key
            if timestamp >= start_utc:
                walk(node.left)
            if start_utc <= timestamp <= end_utc:
                result.append(node.workout)
            if timestamp <= end_utc:
                walk(node.right)

        walk(self.root)
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
            if abs(left-right) > 1 or node.height != 1 + max(left, right):
                raise AssertionError('AVL balance/height broken')
            return node.height
        check(self.root)
        return True
