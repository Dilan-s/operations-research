import numpy as np


class Simplex:
    def __init__(self, obj, arr, rhs, BVs, all_vars):
        self.obj = obj
        self.arr = arr
        self.rhs = rhs
        self.BVs = BVs
        self.all_vars = all_vars

    def run(self):
        self.to_solver_format()
        print(self)
        done = max(self.obj[1:]) <= 0
        while not done:
            objs = np.array(self.obj[1:])
            max_index = np.argmax(objs) + 1
            print("Pivot Column:", self.all_vars[max_index])
            min_blocker = 1000
            min_blocker_index = -1
            curr_row = []
            for i, numerator in enumerate(self.rhs[1:]):

                denominator = self.arr[i][max_index]
                if denominator > 0:
                    value = (numerator / denominator)
                    if min_blocker > value:
                        min_blocker = value
                        min_blocker_index = i + 1
                        curr_row = self.arr[i].copy()

            print("Pivot Row", self.BVs[min_blocker_index])

            scale = self.obj[max_index] / curr_row[max_index]
            for i in range(len(self.obj)):
                self.obj[i] = self.obj[i] - curr_row[i] * scale
            self.rhs[0] = self.rhs[0] - self.rhs[min_blocker_index] * scale

            for i in range(len(self.arr)):
                if i + 1 != min_blocker_index:
                    scale = self.arr[i][max_index] / curr_row[max_index]
                    for j in range(len(self.arr[i])):
                        self.arr[i][j] = self.arr[i][j] - curr_row[j] * scale
                    self.rhs[i + 1] = self.rhs[i + 1] - self.rhs[min_blocker_index] * scale

            i = min_blocker_index - 1
            for j in range(len(self.arr[i])):
                self.arr[i][j] = self.arr[i][j] / curr_row[max_index]
            self.rhs[i + 1] = self.rhs[i + 1] / curr_row[max_index]

            self.BVs[min_blocker_index] = self.all_vars[max_index]

            print(self)
            done = max(self.obj[1:]) <= 0

    def to_solver_format(self):
        for i in self.all_vars[1:]:
            print("var", i, ">= 0;")

        print("minimize", self.all_vars[0] + ":",
              " + ".join([str(coef) + "*" + var for (coef, var) in zip(self.obj[1:], self.all_vars[1:])]) + ";")

        for ind, arr in enumerate(self.arr):
            print("subject to c" + str(ind) + ":",
                  " + ".join([str(coef) + "*" + var for (coef, var) in zip(arr[1:], self.all_vars[1:])]) + " = " + str(
                      self.rhs[ind + 1]) + ";")
        print("end;")

    def __str__(self):
        res = ["BV | " + "  | ".join(self.all_vars) + " | RHS"]
        for i, v in enumerate(self.BVs):
            if i == 0:
                s = v + " | " + " | ".join([str(round(float(x), 2)) for x in self.obj]) + " | " + str(
                    round(self.rhs[i], 2))
            else:
                s = v + " | " + " | ".join([str(round(float(x), 2)) for x in self.arr[i - 1]]) + " | " + str(
                    round(self.rhs[i], 2))
            res.append(s)
        return "\n".join(res)


if __name__ == '__main__':
    s = Simplex([1, -4, 6, 0, 0, 0], [[0, -1, 1, 1, 0, 0], [0, 1, 3, 0, 1, 0], [0, 3, 1, 0, 0, 1]],
                [0, 1, 9, 15], ["x0", "x3", "x4", "x5"], ["x0", "x1", "x2", "x3", "x4", "x5"])
    s.run()
