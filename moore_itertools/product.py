from typing import Iterable, Iterator, Tuple, TypeVar

TypeA = TypeVar("A")
TypeB = TypeVar("B")


def product(iterable1: Iterable[A], iterable2: Iterable[B]) -> Iterator[Tuple[A, B]]:
    """Return the cartesian product of two iterables, iterable1 and iterable2,
    in such a way that either or both can be infinite, or at least very large.

    Values from the iterables are memoized until they are no longer needed.
    This is good for expensive generators, if your generation is cheap there's
    better ways.

    Results are yielded in an arbitrary order:

    >>> sorted(list(product('abc', '1234')))  # doctest: +NORMALIZE_WHITESPACE
    [('a', '1'), ('a', '2'), ('a', '3'), ('a', '4'),
    ('b', '1'), ('b', '2'), ('b', '3'), ('b', '4'),
    ('c', '1'), ('c', '2'), ('c', '3'), ('c', '4')]

    Having infinite generators as inputs, even as both inputs, is fine so long
    as you can handle infinite output:

    >>> from itertools import count, islice
    >>> len(list(islice(product(count(0),count(0)), 1000000)))
    1000000

    Empty iterators do what you'd expect, even with infinite generators:

    >>> list(product([], count(0)))
    []

    """
    gen1 = iter(iterable1)
    gen2 = iter(iterable2)

    # grab the first value off each iterator.  If either are
    # empty, the result is empty so just return.
    try:
        val1 = next(gen1)
        val2 = next(gen2)
        yield val1, val2
    except StopIteration:
        return

    # remember the values we've seen so far.  When a new value
    # arrives on either iterator we'll use these to fill in the
    # blanks.
    mem1 = [val1]
    mem2 = [val2]

    while True:
        # we go around this loop for as long as both
        # gen1 and gen2 are producing new values, taking
        # it in turns and filling in missing values.
        try:
            val1 = next(gen1)
            yield from ((val1, val2) for val2 in mem2)
            mem1.append(val1)
        except StopIteration:
            # mem2 is no longer necessary so throw it away
            # to reduce memory usage.
            del mem2

            # gen1 is exhausted, so from here on in we just
            # take values from gen2 and yield them with the
            # mem1 values we took from gen1 already.
            for val2 in gen2:
                yield from ((val1, val2) for val1 in mem1)
            return

        # same thing, opposite roles.
        try:
            val2 = next(gen2)
            yield from ((val1, val2) for val1 in mem1)
            mem2.append(val2)
        except StopIteration:
            del mem1
            for val1 in gen1:
                yield from ((val1, val2) for val2 in mem2)
            return
