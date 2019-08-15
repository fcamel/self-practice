#!/usr/bin/env python
# -*- encoding: utf8 -*-

import random

# A simple randomized algorithm: estimate PI using samples.
# Simulate sampling a point inside a square and a circle.
# The center of the square and the circle is the same,
# and the width othe square is 2r where r is the radius of the circle.
def pi(n):
    r = 0.5
    r_square = r * r
    center_x = 0.5
    center_y = 0.5
    inside_circle = 0
    for _ in range(n):
        x = random.random()
        y = random.random()
        dx = x - center_x
        dy = y - center_y
        if dx*dx + dy*dy < r_square:
            inside_circle += 1

    # inside_circle / n ~= (r^2 * PI) / (2r)^2 = PI/4
    return 4.0 * inside_circle / n

if __name__ == '__main__':
    print(pi(1000000))
