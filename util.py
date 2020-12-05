def uniq_c(lst):
    out = {}
    for x in lst:
        if not x in out:
            out[x] = 0
        out[x] += 1
    return out
