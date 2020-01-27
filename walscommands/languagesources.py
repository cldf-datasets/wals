"""
Re-compute language sources from valuesetrefernces
"""
import collections

from cldfbench_wals import Dataset


def register(parser):
    pass


def run(args):
    ds = Dataset()

    vsrefs = collections.defaultdict(set)
    for row in ds.iter_rows('valuesetreference.csv', lambda r: True):
        vsrefs[row['valueset_pk']].add(row['source_pk'])

    lrefs = collections.defaultdict(set)
    for row in ds.iter_rows('valueset.csv', lambda r: r['pk'] in vsrefs):
        lrefs[row['language_pk']] = lrefs[row['language_pk']].union(vsrefs[row['pk']])

    def repl(r):
        if r['language_pk'] in lrefs:
            if r['source_pk'] in lrefs[r['language_pk']]:
                lrefs[r['language_pk']].remove(r['source_pk'])
                return r
    ds.rewrite('languagesource.csv', repl)

    rows = []
    pk = ds.maxpk('languagesource.csv')
    for lpk in sorted(lrefs):
        for spk in sorted(lrefs[lpk]):
            pk += 1
            rows.append([pk, '', lpk, spk, '1'])
    ds.add_rows('languagesource.csv', *rows)
