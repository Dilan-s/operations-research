import math

import numpy as np


class Fraction:
    def __init__(self, num, den=1):
        factor = math.gcd(num, den)
        self.num = int(num / factor)
        self.den = int(den / factor)
        if self.den < 0:
            self.num = -self.num
            self.den = -self.den

    def __add__(self, other):
        if isinstance(other, Fraction):
            return Fraction(int(self.num * other.den) + int(self.den * other.num), int(self.den * other.den))
        if isinstance(other, int):
            return self + Fraction(other)
        raise Exception("add got unexpected type")

    def __mul__(self, other):
        if isinstance(other, Fraction):
            return Fraction(int(self.num * other.num), int(self.den * other.den))
        if isinstance(other, int):
            return self * Fraction(other)
        raise Exception("add got unexpected type")

    def __sub__(self, other):
        if isinstance(other, Fraction):
            return Fraction(int(self.num * other.den) - int(self.den * other.num), int(self.den * other.den))
        if isinstance(other, int):
            return self - Fraction(other)
        raise Exception("add got unexpected type")

    def __truediv__(self, other):
        if isinstance(other, Fraction):
            return self * Fraction(other.den, other.num)
        if isinstance(other, int):
            return self / Fraction(other)
        raise Exception("add got unexpected type")

    def __lt__(self, other):
        f = self - other
        return f.num < 0

    def __le__(self, other):
        f = self - other
        return f.num <= 0

    def __eq__(self, other):
        f = self - other
        return f.num == 0

    def __ne__(self, other):
        f = self - other
        return f.num != 0

    def __gt__(self, other):
        f = self - other
        return f.num > 0

    def __ge__(self, other):
        f = self - other
        return f.num >= 0

    def toInput(self):
        if self.den == 1:
            return str(self.num)
        return "Fraction(" + str(self.num) + ", " + str(self.den) + ")"

    def __str__(self):
        if self.den == 1:
            return str(self.num)
        else:
            return str(self.num) + "/" + str(self.den)


class Simplex:
    def __init__(self, obj, arr, rhs, BVs, all_vars):
        self.obj = [x if isinstance(x, Fraction) else Fraction(x) for x in obj]
        self.arr = [[x if isinstance(x, Fraction) else Fraction(x) for x in ar] for ar in arr]
        self.rhs = [x if isinstance(x, Fraction) else Fraction(x) for x in rhs]
        self.BVs = BVs
        self.all_vars = all_vars

    def run_simplex(self):
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
              " + ".join(
                  [str(coef * -1) + "*" + var for (coef, var) in zip(self.obj[1:], self.all_vars[1:])]) + " + " + str(
                  self.rhs[0]) + ";")

        for ind, arr in enumerate(self.arr):
            print("subject to c" + str(ind) + ":",
                  " + ".join([str(coef) + "*" + var for (coef, var) in zip(arr[1:], self.all_vars[1:])]) + " = " + str(
                      self.rhs[ind + 1]) + ";")
        print("end;")

    def toInput(self):
        z = "z = [" + ", ".join([x.toInput() for x in self.obj]) + "]"
        b = "b = ["
        f = True
        for arr in self.arr:
            if not f:
                b += ", "
            f = False
            b += "[" + ", ".join([x.toInput() for x in arr]) + "]"
        b += "]"
        rhs = "rhs = [" + ", ".join([x.toInput() for x in self.rhs]) + "]"
        bvs = "bvs = " + str(self.BVs)
        var = "var = " + str(self.all_vars)
        s = "\n".join("\t" + x for x in [z, b, rhs, bvs, var])
        return s

    def __str__(self):
        res = ["BV | " + " | ".join(self.all_vars) + " | RHS"]
        for i, v in enumerate(self.BVs):
            if i == 0:
                s = v + " | " + " | ".join([str(x) for x in self.obj]) + " | " + str(self.rhs[i])
            else:
                s = v + " | " + " | ".join([str(x) for x in self.arr[i - 1]]) + " | " + str(self.rhs[i])
            res.append(s)
        return "\n".join(res)


if __name__ == '__main__':
    z = [1, 1, 4, 0, 0]
    b = [[0, 2, 4, 1, 0],[0, 10, 3, 0, 1]]
    rhs = [0, 7, 14]
    bvs = ["z ", "x3", "x4"]
    var = ["z ", "x1", "x2", "x3", "x4"]
    s = Simplex(z,
                b,
                rhs,
                bvs,
                var)
    s.run_simplex()
    print(s.toInput())
