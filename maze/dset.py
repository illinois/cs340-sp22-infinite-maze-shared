class DSet:

    def __init__(self, n):
        self.arr = [-1] * n
        self.n = n

    def find(self, i):
        if i < 0 or i >= self.n:
            return -1

        if self.arr[i] < 0:
            return i

        return self.find(self.arr[i])

    def union(self, i, j):
        i_root_idx = self.find(i)
        j_root_idx = self.find(j)
        new_size = self.arr[i_root_idx] + self.arr[j_root_idx]

        if self.arr[i_root_idx] < self.arr[j_root_idx]:
            self.arr[i_root_idx] = new_size
            self.arr[j_root_idx] = i_root_idx
        else:
            self.arr[j_root_idx] = new_size
            self.arr[i_root_idx] = j_root_idx

    def size(self, i):
        return -self.arr[self.find(i)]


if __name__ == '__main__':
    ds = DSet(10)

    ds.union(2, 4)
    print(ds.arr)
    print(ds.size(1))

    ds.union(1, 2)

    print(ds.size(2))

    assert(ds.find(4) == ds.find(1))

    ds.union(9, 2)

    print(ds.arr)

    print([ds.size(i) for i in range(ds.n)])
