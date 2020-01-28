"""

"""
from cldfbench_wals import Dataset


def register(parser):
    parser.add_argument('language_id')
    parser.add_argument('--replacement_id')


def run(args):
    ds = Dataset()
    lpk = ds.pk_from_id('language.csv', args.language_id)

    for t in ['languagesource', 'languageidentifier', 'countrylanguage']:
        ds.rewrite(t + '.csv', lambda r: r if r['language_pk'] != lpk else None)

    for t in ['language', 'walslanguage']:
        ds.rewrite(t + '.csv', lambda r: r if r['pk'] != lpk else None)

    if args.replacement_id:
        rpk = ds.pk_from_id('language.csv', args.replacement_id)
    else:
        rpk = None

    def repl(r):
        if r['language_pk'] == lpk:
            if rpk:
                r['language_pk'] = rpk
            else:
                args.log.warning('removing sentence {0}'.format(r))
                return
        return r
    ds.rewrite('sentence.csv', repl)
