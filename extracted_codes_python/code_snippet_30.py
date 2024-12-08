#!/usr/bin/python3
"""prime factorization of a list of numbers from a file"""
import sys
import time
from math import sqrt, ceil


# function to check if a number is prime
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True


# function to factor a single RSA number using the trial division method
def factor_rsa_number(num):
    factors = []
    while num % 2 == 0:
        factors.append(2)
        num = num // 2
    i = 3
    while i <= sqrt(num):
        if num % i == 0:
            factors.append(i)
            num //= i
        else:
            i = i + 2
    if num > 2:
        factors.append(num)
    if len(factors) == 1:
        p = factors[0]
        q = num // p
        return (p, q)
    else:
        prodquot = []
        for factor in factors:
            if is_prime(factor):
                prodquot.append(factor)
            else:
                p, q = factor_rsa_number(factor)
                prodquot.append(p)
                prodquot.append(q)
        return tuple(prodquot)


input = sys.argv[1]
with open(input, 'r') as f:
    rsa_nums = [int(line.strip()) for line in f.readlines()]
start = time.time()
for num in rsa_nums:
    p, q = factor_rsa_number(num)
    print(f"{num}={q}*{p}")
end_time = time.time()
exec_time = end_time - start
