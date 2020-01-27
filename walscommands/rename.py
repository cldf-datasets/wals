"""

"""
from clldutils.misc import slug

from cldfbench_wals import Dataset


def register(parser):
    parser.add_argument('language_id')
    parser.add_argument('name')


def run(args):
    ds = Dataset()
    lpk = ds.pk_from_id('language', args.language_id)

    def _rename(r):
        if r['pk'] == lpk:
            if 'name' in r:
                r['name'] = args.name
            if 'ascii_name' in r:
                r['ascii_name'] = slug(args.name, remove_whitespace=False)
        return r

    ds.rewrite('language.csv', _rename)
    ds.rewrite('walslanguage.csv', _rename)
