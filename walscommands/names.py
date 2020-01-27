"""
cldfbench wals.names bia ...
"""
from cldfbench_wals import Dataset


def register(parser):
    parser.add_argument('language_id')
    parser.add_argument('codes', nargs='+', help="(other|ethnologue)=NAME pairs")


def run(args):
    ds = Dataset()
    lpk = ds.pk_from_id('language', args.language_id)

    ipks = set()
    for code in args.codes:
        t, code = code.split('=', maxsplit=1)
        assert t in ['other', 'ethnologue']
        # Check whether the code exists:
        ipk = None
        for row in ds.iter_rows(
                'identifier.csv',
                lambda r: r['type'] == 'name' and r['description'] == t and r['name'] == code):
            ipk = row['pk']
            break

        if not ipk:
            # create an identifier:
            ipk = ds.maxpk('identifier.csv') + 1
            ds.add_rows('identifier.csv', [ipk, '', code, t, '', code, 'name', 'en', '1'])

        ipks.add(ipk)

    # Now rewrite languageidentifier.csv:
    keep = set()
    for row in ds.iter_rows('languageidentifier.csv', lambda r: r['language_pk'] == lpk):
        # get the identifier data:
        if row['identifier_pk'] in ipks:
            keep.add(row['identifier_pk'])
            ipks.remove(row['identifier_pk'])
            continue
        i = ds.get_row('identifier.csv', lambda r: r['pk'] == row['identifier_pk'])
        if (i['type'] != 'name') or (i['description'] not in ('other', 'ethnologue')):
            keep.add(row['identifier_pk'])

    def repl(r):
        if r['language_pk'] != lpk or r['identifier_pk'] in keep:
            return r

    ds.rewrite('languageidentifier.csv', repl)
    if ipks:
        # We have to create additional languageidentifier!
        lipk = ds.maxpk('languageidentifier.csv') + 1
        ds.add_rows(
            'languageidentifier.csv',
            *[[lipk + j, '', lpk, ipk, '', '1'] for j, ipk in enumerate(ipks)])
