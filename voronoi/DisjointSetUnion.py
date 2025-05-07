class DisjointSetUnion:
    def __init__(self, size):
        self.p = list(range(size))  # массив родителей
        self.r = [0] * size         # массив рангов


    def union(self, x, y):
        x_root = self.get(x)
        y_root = self.get(y)
        if x_root == y_root:
            return
        if self.r[x_root] == self.r[y_root]:
            self.r[x_root] += 1
        if self.r[x_root] < self.r[y_root]:
            self.p[x_root] = y_root
        else:
            self.p[y_root] = x_root

    def get(self, x):
        root = x
        while self.p[root] != root:
            root = self.p[root]
        while self.p[x] != x:
            parent = self.p[x]
            self.p[x] = root
            x = parent
        return root