"""
Re-compute language sources from valuesetrefernces
"""
import collections

from cldfbench_wals import Dataset


def register(parser):
    pass


def run(args):
    ds = Dataset()

    lpk2id = {}
    for row in ds.iter_rows('language.csv', lambda r: True):
        lpk2id[row['pk']] = row['id']

    vspk2lid = {}
    vschange = set()
    for row in ds.iter_rows('valueset.csv', lambda r: True):
        vspk2lid[row['pk']] = lpk2id[row['language_pk']]
        if not row['id'].endswith('-' + lpk2id[row['language_pk']]):
            vschange.add(row['pk'])

    vchange = set()
    for row in ds.iter_rows('value.csv', lambda r: True):
        if not row['id'].endswith('-' + vspk2lid[row['valueset_pk']]):
            vchange.add(row['pk'])

    def rvs(row):
        if row['pk'] in vschange:
            row['id'] = row['id'].split('-')[0] + '-' + lpk2id[row['language_pk']]
        return row
    ds.rewrite('valueset.csv', rvs)

    def rv(row):
        if row['pk'] in vchange:
            row['id'] = row['id'].split('-')[0] + '-' + vspk2lid[row['valueset_pk']]
        return row
    ds.rewrite('value.csv', rv)