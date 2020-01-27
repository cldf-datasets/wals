"""
Switch datapoints - specified by reference - from one language to another

switchdata old_lang reference new_lang

$ cldfbench wals.switchdata bia "Meinhof 1938/39" brq
"""
from cldfbench_wals import Dataset

from .fixvids import run as fixvids_run


def register(parser):
    parser.add_argument('from_language_id')
    parser.add_argument('ref')
    parser.add_argument('to_language_id')


def run(args):
    ds = Dataset()

    fpk = ds.pk_from_id('language.csv', args.from_language_id)
    tpk = ds.pk_from_id('language.csv', args.to_language_id)
    spk = ds.get_row('source.csv', cond=lambda r: r['name'] == args.ref)['pk']

    vspks = set()
    for row in ds.iter_rows('valuesetreference.csv', lambda r: r['source_pk'] == spk):
        vspks.add(row['valueset_pk'])

    def repl(r):
        if r['language_pk'] == fpk and r['pk'] in vspks:
            r['language_pk'] = tpk
        return r
    ds.rewrite('valueset.csv', repl)
    fixvids_run(args)
