#!/usr/bin/env python
import copy
import doctest
import logging
import re
import sys
from collections import deque


log = logging.getLogger(__name__).debug


# Part One


def part_one():
    print("Part One")
    assert 306 == play(data[0])
    # Not 30433 oops
    print(play(data[1]))


def play(data, recursive=False):
    deck_a, deck_b = load(data)
    if recursive:
        deck_a, deck_b = settle_recursive(deck_a, deck_b)
        return score_recursive(deck_a, deck_b)
    else:
        deck_a, deck_b = settle(deck_a, deck_b)
        return score(deck_a, deck_b)


def load(data):
    one, two = data.split("\n\n")

    def nums(d):
        return deque([int(line) for line in d.splitlines()[1:]])

    return nums(one), nums(two)


def settle(deck_a, deck_b):
    rounds = 0
    while len(deck_a) and len(deck_b):
        rounds += 1
        log(f"\nRound {rounds}:\ndeck_a: {deck_a}\ndeck_b: {deck_b}\n")
        card_a, card_b = deck_a.popleft(), deck_b.popleft()
        if card_a > card_b:
            deck_a.extend((card_a, card_b))
        else:
            deck_b.extend((card_b, card_a))
    return deck_a, deck_b


def score(deck_a, deck_b):
    deck = deck_a if deck_a else deck_b
    return sum(((i + 1) * card) for i, card in enumerate(reversed(deck)))


# Part Two


def part_two():
    print("Part Two")
    assert 291 == play(data[0], recursive=True)
    print(play(data[1], recursive=True))


game = 0


def settle_recursive(deck_a, deck_b):
    global game
    game += 1
    _game = game
    playlog = set()
    rounds = 0
    while len(deck_a) and len(deck_b):
        rounds += 1
        log(f"Round {rounds} (Game {_game}):\ndeck_a: {deck_a}\ndeck_b: {deck_b}\n")

        # Check for early out.
        decks = tuple(deck_a), tuple(deck_b)
        if decks in playlog:
            # Is this what they mean by instantly ends with win for player 1??
            log("EARLY EXIT")
            break
        else:
            playlog.add(decks)

        card_a, card_b = deck_a.popleft(), deck_b.popleft()
        if card_a <= len(deck_a) and card_b <= len(deck_b):
            # Recursive game
            rec_deck_a, rec_deck_b = settle_recursive(
                deque(x for i, x in enumerate(deck_a) if i < card_a),
                deque(x for i, x in enumerate(deck_b) if i < card_b),
            )
            if len(rec_deck_a):
                deck_a.extend((card_a, card_b))
            else:
                deck_b.extend((card_b, card_a))
        elif card_a > card_b:
            deck_a.extend((card_a, card_b))
        else:
            deck_b.extend((card_b, card_a))
    return deck_a, deck_b


def score_recursive(deck_a, deck_b):
    if deck_a and deck_b:
        deck = deck_a  # Must have been an early exit, Player 1 wins?
    else:
        deck = deck_a if deck_a else deck_b
    return sum(((i + 1) * card) for i, card in enumerate(reversed(deck)))


# Data

data = []
data.append(
    """Player 1:
9
2
6
3
1

Player 2:
5
8
4
7
10"""
)
data.append(
    """Player 1:
50
19
40
22
7
4
3
16
34
45
46
39
44
32
20
29
15
35
41
2
21
28
6
26
48

Player 2:
14
9
37
47
38
27
30
24
36
31
43
42
11
17
18
10
12
5
33
25
8
23
1
13
49"""
)

if __name__ == "__main__":

    def main(part=None):
        if not part or part == 1:
            part_one()
        if not part or part == 2:
            part_two()

    doctest.testmod(verbose=False)
    if len(sys.argv) > 1:
        if len(sys.argv) > 2 and sys.argv[2] in ("-v", "--verbose"):
            logging.basicConfig(level=logging.DEBUG)
        main(part=int(sys.argv[1]))
    else:
        main()
