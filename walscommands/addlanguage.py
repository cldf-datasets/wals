"""
Add a new language
"""
from clldutils.misc import slug

from cldfbench_wals import Dataset


def register(parser):
    parser.add_argument('language_id')
    parser.add_argument('name')
    parser.add_argument('genus')
    # lat,long
    parser.add_argument('--latitude', type=float)
    parser.add_argument('--longitude', type=float)
    # macroarea
    parser.add_argument('--macroarea', default=None, choices=[
        'Africa',
        'Australia',
        'Eurasia',
        'North America',
        'Papunesia',
        'South America',
    ])


def run(args):
    ds = Dataset()
    assert not list(ds.iter_rows('language.csv', lambda r: r['id'] == args.language_id))

    lpk = ds.maxpk('language.csv') + 1
    gpk = ds.get_row('genus.csv', lambda r: r['name'] == args.genus)['pk']

    #pk, jsondata, id, name, description, markup_description, latitude, longitude, version
    #353,, ktz, Kati( in Afghanistan), , , 35.5, 70, 1
    ds.add_rows(
        'language.csv',
        [
            lpk,
            '',
            args.language_id,
            args.name,
            '',
            '',
            args.latitude or '',
            args.longitude or '',
            '1',
        ])

    #pk,ascii_name,genus_pk,samples_100,samples_200,iso_codes,macroarea
    #910,amis,595,f,f,ami,Papunesia
    ds.add_rows(
        'walslanguage.csv',
        [
            lpk,
            slug(args.name, remove_whitespace=False),
            gpk,
            'f',
            'f',
            '',
            args.macroarea,
            ],
    )
