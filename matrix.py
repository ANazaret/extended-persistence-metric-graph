import collections


class Matrix:
    """
    Sparse representation of **binary** matrices using dict(set)
    matrix is a dict of columns
    columns is a sorted list of id (sorted before reduction), if id is in the list, then M(id,column) = 1
    Otherwise 0
    """

    def __init__(self, dimension):
        self.data = collections.defaultdict(list)
        self.dimension = dimension

    def set_one(self, i, j):
        self.data[j].append(i)

    def get_zero_columns(self):
        return set(range(self.dimension)).difference(set(self.data.keys()))

    def reduce(self):
        for l in self.data.values():
            l.sort()

        pivots_row2col = {}
        for col_id in sorted(self.data.keys()):
            column = self.data[col_id]
            while column:
                row_id = column[-1]
                if row_id not in pivots_row2col:
                    # First pivot at this height: we are done for this column
                    pivots_row2col[row_id] = col_id
                    break

                # We already have a pivot at this height, we cancel this one
                other_col_id = pivots_row2col[row_id]

                column = Matrix.sum_columns(column, self.data[other_col_id])
                self.data[col_id] = column

                # Ensure sparse data
            if len(column) == 0:
                self.data.pop(col_id)

        return pivots_row2col

    @staticmethod
    def sum_columns(a, b):
        ai, bi = 0, 0
        result = []
        while ai < len(a) and bi < len(b):
            av = a[ai]
            bv = b[bi]
            if av == bv:
                ai += 1
                bi += 1
            elif av < bv:
                ai += 1
                result.append(av)
            else:
                bi += 1
                result.append(bv)

        return result

    def __str__(self):
        return "\n".join([
            "".join(["1" if col in self.data and i in self.data[col] else "0"
                     for col in range(self.dimension)])
            for i in range(self.dimension)])

    def __repr__(self):
        return self.__str__()
