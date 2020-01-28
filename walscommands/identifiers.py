"""
cldfbench wals.identifiers bia iso=bip glottolog=bila1255
"""
from cldfbench_wals import Dataset


def register(parser):
    parser.add_argument('language_id')
    parser.add_argument('codes', nargs='+', help="(iso|glottolog)=CODE pairs")


def run(args):
    ds = Dataset()
    lpk = ds.pk_from_id('language', args.language_id)
    assert lpk
    iso_codes = set()

    ipks = set()
    for code in args.codes:
        t, code = code.split('=', maxsplit=1)
        assert t in ['iso', 'glottolog']
        if t == 'iso':
            iso_codes.add(code)
            t = 'iso639-3'
        # Check whether the code exists:
        ipk = None
        for row in ds.iter_rows(
                'identifier.csv', lambda r: r['type'] == t and r['name'] == code):
            ipk = row['pk']
            break

        if not ipk:
            # create an identifier:
            ipk = ds.maxpk('identifier.csv') + 1
            ds.add_rows('identifier.csv', [ipk, '', code, '', '', code, t, 'en', '1'])

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
        if i['type'] not in ('iso639-3', 'glottolog'):
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

    # rewrite iso_codes col in walslanguage.csv: ', '.join(sorted(args.isocodes))
    def adj(r):
        if r['pk'] == lpk:
            r['iso_codes'] = ', '.join(sorted(iso_codes))
        return r
    ds.rewrite('walslanguage.csv', adj)
