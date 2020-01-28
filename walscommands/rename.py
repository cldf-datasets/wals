"""

"""
from clldutils.misc import slug

from cldfbench_wals import Dataset


def register(parser):
    parser.add_argument('language_id')
    parser.add_argument('name')
    parser.add_argument('--keep-old-name', default=False, action='store_true')
    parser.add_argument('--latitude', type=float)
    parser.add_argument('--longitude', type=float)
    parser.add_argument('--countries')


def run(args):
    ds = Dataset()
    row = ds.get_row('language.csv', lambda r: r['id'] == args.language_id)
    lpk = row['pk']
    old_name = row['name']

    def _rename(r):
        if r['pk'] == lpk:
            if 'name' in r:
                r['name'] = args.name
            if 'ascii_name' in r:
                r['ascii_name'] = slug(args.name, remove_whitespace=False)
            if args.latitude and 'latitude' in r:
                r['latitude'] = args.latitude
            if args.longitude and 'longitude' in r:
                r['longitude'] = args.longitude
        return r

    ds.rewrite('language.csv', _rename)
    ds.rewrite('walslanguage.csv', _rename)

    if args.countries:
        cpks = set()
        for row in ds.iter_rows(
                'country.csv',
                lambda r:
                r['id'] in args.countries.split(',') or r['name'] in args.countries.split(',')):
            cpks.add(row['pk'])

        #pk, jsondata, country_pk, language_pk
        ds.rewrite('countrylanguage.csv', lambda r: r if r['language_pk'] != lpk else None)
        clpk = ds.maxpk('countrylanguage.csv') + 1
        ds.add_rows(
            'countrylanguage.csv',
            *[[clpk + i, '', cpk, lpk] for i, cpk in enumerate(sorted(cpks))])

    if args.keep_old_name:
        # Check whether the code exists:
        ipk = None
        for row in ds.iter_rows(
                'identifier.csv',
                lambda r:
                r['type'] == 'name' and r['description'] == 'other' and r['name'] == old_name):
            ipk = row['pk']
            break

        if not ipk:
            # create an identifier:
            ipk = ds.maxpk('identifier.csv') + 1
            ds.add_rows('identifier.csv', [ipk, '', old_name, 'other', '', '', 'name', 'en', '1'])

        lipk = ds.maxpk('languageidentifier.csv') + 1
        ds.add_rows(
            'languageidentifier.csv', [lipk, '', lpk, ipk, '', '1'])
