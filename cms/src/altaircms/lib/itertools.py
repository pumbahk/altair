def group_by_n(itr, n):
    """
    >>> L = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(group_by_n(L, 3))
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    >>> L = [1, 2, 3, 4, 5, 6, 7, 8]
    >>> list(group_by_n(L, 3))
    [[1, 2, 3], [4, 5, 6], [7, 8]]
    """
    i = 0
    r = []
    for e in itr:
        r.append(e)
        i += 1
        if i >= n:
            yield r
            r = []
            i = 0
    if i > 0:
        yield r

if __name__ == "__main__":
    import doctest
    doctest.testmod()
