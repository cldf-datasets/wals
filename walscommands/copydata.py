"""
Copy datapoints - specified by reference - from one language to another

copydata old_lang reference new_lang
"""
import collections

from cldfbench_wals import Dataset

from .fixvids import run as fixvids_run
from .languagesources import run as languagesources_run


def register(parser):
    parser.add_argument('from_language_id')
    parser.add_argument('ref')
    parser.add_argument('to_language_id')


def run(args):
    ds = Dataset()

    fpk = ds.pk_from_id('language.csv', args.from_language_id)
    tpk = ds.pk_from_id('language.csv', args.to_language_id)
    spk = ds.get_row('source.csv', cond=lambda r: r['name'] == args.ref)['pk']

    vspk_map = {}
    # Collect PKs for all valuesets that are referenced by the specified source and possibly
    # need to be copied and vsr pks for later updating!
    vspk2vsrekpk = collections.defaultdict(list)
    for row in ds.iter_rows('valuesetreference.csv', lambda r: r['source_pk'] == spk):
        vspk2vsrekpk[row['valueset_pk']].append(row['pk'])

    # Now read valueset.csv and value.csv for these:
    valueset, value = {}, {}

    for row in ds.iter_rows('valueset.csv', lambda r: r['pk'] in vspk2vsrekpk):
        # must limit vspks to the correct language, too!
        if row['language_pk'] == fpk:
            valueset[row['pk']] = row
        elif row['pk'] in vspk2vsrekpk:
            del vspk2vsrekpk[row['pk']]

    print(len(vspk2vsrekpk))

    for row in ds.iter_rows('value.csv', lambda r: r['valueset_pk'] in vspk2vsrekpk):
        value[row['valueset_pk']] = row

    # Now write the copied data:
    vspk = ds.maxpk('valueset.csv')
    rows = []
    for oldpk, row in valueset.items():
        # first check, whether a valueset for this datapoint already exist for the target
        # language!
        expk = ds.pk_from_id(
            'valueset.csv', row['id'].replace(args.from_language_id, args.to_language_id))
        if expk:
            print('exists')
            vspk_map[oldpk] = expk
        else:
            vspk += 1
            vspk_map[oldpk] = str(vspk)
            # Update pk and language_pk
            row['pk'] = vspk
            row['id'] = row['id'].replace(args.from_language_id, args.to_language_id)
            row['language_pk'] = tpk
            rows.append(row.values())
    ds.add_rows('valueset.csv', *rows)

    vpk = ds.maxpk('value.csv')
    rows = []
    for oldpk, row in value.items():
        # first check, whether a valueset for this datapoint already exist for the target
        # language!
        expk = ds.pk_from_id(
            'value.csv', row['id'].replace(args.from_language_id, args.to_language_id))
        if not expk:
            vpk += 1
            row['pk'] = vpk
            row['id'] = row['id'].replace(args.from_language_id, args.to_language_id)
            row['valueset_pk'] = vspk_map[oldpk]
            rows.append(row.values())
    ds.add_rows('value.csv', *rows)

    #
    # FIXME: now update valuesetreference.csv
    #
    all_vsrefpks = set()
    for s in vspk2vsrekpk.values():
        all_vsrefpks = all_vsrefpks.union(s)

    def upd(r):
        if r['pk'] in all_vsrefpks:
            r['valueset_pk'] = vspk_map[r['valueset_pk']]
        return r
    ds.rewrite('valuesetreference.csv', upd)
    fixvids_run(args)
    languagesources_run(args)
