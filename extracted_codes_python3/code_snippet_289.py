""" Advent of code 2021 day 11 / 1 """

from os import path
import math
from functools import reduce

pos = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (-1, -1), (1, -1), (1, 1)]


class Code(object):
    def __init__(self, lines):
        self.lines = lines
        self.height = len(lines)
        self.width = len(lines[0])

    def fillpos(self, y, x):
        pl = []
        for (dy, dx) in pos:
            ny = dy+y
            nx = dx + x
            np = (ny, nx)
            if ny >= 0 and ny < self.height and nx >= 0 and nx < self.width:
                pl.append(np)
        return pl

    def printlines(self, msg):
        pass
        # print(msg)
        # for line in self.lines:
        #     print("".join(map(str,['+' if x>9 else x for x in line])))
            
    def flash(self, coord, flashing):
        new_points = self.fillpos(*coord) 
        flashing.add(coord)
        res = 1
        for newc in new_points:
            [y,x] = newc
            self.lines[y][x] += 1
            if self.lines[y][x] > 9 and newc not in flashing:
                res += self.flash(newc, flashing)
        return res

    def solve(self):
        """
        First, the energy level of each octopus increases by 1.
        Then, any octopus with an energy level greater than 9 flashes.
        This increases the energy level of all adjacent octopuses by 1,
        including octopuses that are diagonally adjacent. 
        If this causes an octopus to have an energy level greater than 9, 
        it also flashes. 
        This process continues as long as new octopuses keep having their energy level increased beyond 9.
        (An octopus can only flash at most once per step.)
        Finally, any octopus that flashed during this step has its energy level set to 0, as it used all of its energy to flash.
        """
        # print(self.lines)
        flashes = 0
        steps = 100
        # self.printlines("Before any steps:")
        for i in range(1, steps + 1):
            # print(f"iteration {i}", flashes)
            flashing = set()
            for y, line in enumerate(self.lines):
                for x, energy in enumerate(line):
                    self.lines[y][x] += 1
            for y, line in enumerate(self.lines):
                for x, energy in enumerate(line):
                    if self.lines[y][x] > 9 and (y,x) not in flashing:
                       flashes += self.flash((y,x), flashing)
            self.printlines(f"After flash: {i}")
            for [y, x] in flashing:
                self.lines[y][x] = 0
            self.printlines(f"After reset: {i}")
        return flashes


def preprocess(raw_data):
    # pattern = re.compile(r'(\w+) (\d+)')
    processed_data = []
    for line in raw_data.split("\n"):
        # match = re.match(pattern, line)
        # data = [match.group(1), match.group(2)]
        data = line
        processed_data.append(list(map(int, data)))
    return processed_data


def solution(data):
    """ Solution to the problem """
    lines = preprocess(data)
    solver = Code(lines)
    return solver.solve()


if __name__ == "__main__":
    with(open(path.join(path.dirname(__file__), 'input.txt'), 'r')) as input_file:
        print(solution(input_file.read()))
