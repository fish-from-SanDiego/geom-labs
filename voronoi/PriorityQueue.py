from typing import List, Optional


class PriorityQueue:
    def __init__(self):
        self._elements: List = list()

    def is_empty(self) -> bool:
        return not self._elements

    def pop(self):
        self._swap(0, len(self._elements) - 1)
        top = self._elements.pop()
        self._sift_down(0)
        return top

    def push(self, elem) -> None:
        elem.index = len(self._elements)
        self._elements.append(elem)
        self._sift_up(len(self._elements) - 1)

    def update(self, i: int) -> None:
        parent = self._get_parent(i)
        if parent >= 0 and self._elements[parent] < self._elements[i]:
            self._sift_up(i)
        else:
            self._sift_down(i)

    def remove(self, i: int) -> None:
        self._swap(i, len(self._elements) - 1)
        self._elements.pop()
        if i < len(self._elements):
            self.update(i)

    def print(self, i: int = 0, tabs: str = "") -> None:
        if i < len(self._elements):
            print(f"{tabs}{self._elements[i]}")
            self.print(self._get_left_child(i), tabs + "\t")
            self.print(self._get_right_child(i), tabs + "\t")

    def _get_parent(self, i: int) -> int:
        return (i + 1) // 2 - 1

    def _get_left_child(self, i: int) -> int:
        return 2 * (i + 1) - 1

    def _get_right_child(self, i: int) -> int:
        return 2 * (i + 1)

    def _sift_down(self, i: int) -> None:
        left = self._get_left_child(i)
        right = self._get_right_child(i)
        j = i
        if left < len(self._elements) and self._elements[j] < self._elements[left]:
            j = left
        if right < len(self._elements) and self._elements[j] < self._elements[right]:
            j = right
        if j != i:
            self._swap(i, j)
            self._sift_down(j)

    def _sift_up(self, i: int) -> None:
        parent = self._get_parent(i)
        if parent >= 0 and self._elements[parent] < self._elements[i]:
            self._swap(i, parent)
            self._sift_up(parent)

    def _swap(self, i: int, j: int) -> None:
        self._elements[i], self._elements[j] = self._elements[j], self._elements[i]
        self._elements[i].index = i
        self._elements[j].index = j
