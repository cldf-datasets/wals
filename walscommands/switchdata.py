"""
Switch datapoints - specified by reference - from one language to another

switchdata old_lang reference new_lang

$ cldfbench wals.switchdata bia "Meinhof 1938/39" brq
"""
from cldfbench_wals import Dataset

from .fixvids import run as fixvids_run
from .languagesources import run as languagesources_run


def register(parser):
    parser.add_argument('from_language_id')
    parser.add_argument('to_language_id')
    parser.add_argument('--ref', default=None)


def run(args):
    ds = Dataset()

    fpk = ds.pk_from_id('language.csv', args.from_language_id)
    tpk = ds.pk_from_id('language.csv', args.to_language_id)
    assert fpk and tpk
    spk = ds.get_row('source.csv', cond=lambda r: r['name'] == args.ref)['pk'] if args.ref else None

    vspks = set()
    vsrpks = set()
    if args.ref:
        for row in ds.iter_rows('valuesetreference.csv', lambda r: r['source_pk'] == spk):
            vsrpks.add(row['valueset_pk'])
    for row in ds.iter_rows('valueset.csv', lambda r: r['language_pk'] == fpk and (r['pk'] in vsrpks or (not args.ref))):
        vspks.add(row['pk'])

    print(len(vspks))

    #
    # FIXME: Determine whether there are any sentences related to values of the valuesets. If so,
    # change the language_pk of the sentence!
    #
    vpks = set()
    for row in ds.iter_rows('value.csv', lambda r: r['valueset_pk'] in vspks):
        vpks.add(row['pk'])

    spks = set()
    for row in ds.iter_rows('valuesentence.csv', lambda r: r['value_pk'] in vpks):
        spks.add(row['sentence_pk'])

    def repl(r):
        if r['language_pk'] == fpk and r['pk'] in spks:
            r['language_pk'] = tpk
        return r
    ds.rewrite('sentence.csv', repl)

    def repl(r):
        if r['language_pk'] == fpk and (r['pk'] in vspks or (args.ref is None)):
            r['language_pk'] = tpk
        return r
    ds.rewrite('valueset.csv', repl)
    fixvids_run(args)
    languagesources_run(args)
