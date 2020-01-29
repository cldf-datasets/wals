"""

"""
from clldutils.misc import slug

from cldfbench_wals import Dataset


def register(parser):
    parser.add_argument('language_id')
    parser.add_argument('genus')
    parser.add_argument('--family', default=None)
    parser.add_argument('--subfamily', default=None)
    parser.add_argument('--icon', default='fcccccc')


def run(args):
    ds = Dataset()
    for lid in args.language_id.split(','):
        recl(ds, lid.strip(), args)


def recl(ds, lid, args):
    lpk = ds.pk_from_id('language.csv', lid)
    if not lpk:
        for row in ds.iter_rows('language.csv', lambda r: r['name'] == lid):
            lpk = row['pk']
            break
    assert lpk, 'language {0} not found'.format(lid)

    wlang = ds.get_row('walslanguage.csv', lambda r: r['pk'] == lpk)

    if not args.family:
        # determine the family from the old genus
        fpk = ds.get_row('genus.csv', lambda r: r['pk'] == wlang['genus_pk'])['family_pk']
    else:
        fpk = None
        for row in ds.iter_rows('family.csv', lambda r: r['name'] == args.family):
            fpk = row['pk']
            break
        if not fpk:
            # Create a new family
            # pk,jsondata,id,name,description,markup_description
            fpk = ds.maxpk('family.csv') + 1
            ds.add_rows('family.csv', [fpk, '', slug(args.family), args.family, '', ''])

    # Find genus:
    gpk = None
    for row in ds.iter_rows('genus.csv', lambda r: r['name'] == args.genus):
        gpk = row['pk']
        break
    if not gpk:
        # Create a new genus
        gpk = ds.maxpk('genus.csv') + 1
        # pk,jsondata,id,name,description,markup_description,family_pk,subfamily,icon
        ds.add_rows(
            'genus.csv', [gpk, '', slug(args.genus), args.genus, '', '', fpk, args.subfamily or '', args.icon])

    def recl(row):
        if row['pk'] == gpk:
            row['family_pk'] = fpk
        return row
    ds.rewrite('genus.csv', recl)

    def recl(row):
        if row['pk'] == lpk:
            row['genus_pk'] = gpk
        return row
    ds.rewrite('walslanguage.csv', recl)
