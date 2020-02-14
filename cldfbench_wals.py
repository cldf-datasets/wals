import re
import json
import pathlib
import itertools
import collections

from csvw import dsv
from cldfbench import Dataset as BaseDataset
from cldfbench import CLDFSpec, Metadata
from pycldf.sources import Source, Reference
from pybtex.database import parse_string


class MetadataWithTravis(Metadata):
    def markdown(self):
        lines, title_found = [], False
        for line in super().markdown().split('\n'):
            lines.append(line)
            if line.startswith('# ') and not title_found:
                title_found = True
                lines.extend([
                    '',
                    "[![Build Status](https://travis-ci.org/cldf-datasets/wals.svg?branch=master)]"
                    "(https://travis-ci.org/cldf-datasets/wals)"
                ])
        return '\n'.join(lines)


def fid_key(fid):
    i = re.search('[A-Z]', fid).start()
    return (int(fid[:i]), fid[i:])


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "wals"
    metadata_cls = MetadataWithTravis

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):
        pass

    def read(self, core, extended=False, pkmap=None, key=None):
        if not key:
            key = lambda d: int(d['pk'])
        res = collections.OrderedDict()
        for row in sorted(self.raw_dir.read_csv('{0}.csv'.format(core), dicts=True), key=key):
            res[row['pk']] = row
            if pkmap is not None:
                pkmap[core][row['pk']] = row['id']
        if extended:
            for row in self.raw_dir.read_csv('{0}.csv'.format(extended), dicts=True):
                res[row['pk']].update(row)
        return res

    def cmd_makecldf(self, args):
        self.create_schema(args.writer.cldf)

        pk2id = collections.defaultdict(dict)
        sources = parse_string(
            self.raw_dir.joinpath('source.bib').read_text(encoding='utf8'), 'bibtex')
        self.read('source', pkmap=pk2id)

        refs = []
        for row in self.raw_dir.read_csv('valuesetreference.csv', dicts=True):
            if row['source_pk']:
                refs.append((row['valueset_pk'], pk2id['source'][row['source_pk']], row['description']))
        srcids = set(r[1] for r in refs)
        args.writer.cldf.add_sources(
            *[Source.from_entry(id_, e) for id_, e in sources.entries.items() if id_ in srcids])

        contributors = self.read('contributor', pkmap=pk2id, key=lambda r: r['id'])
        for row in contributors.values():
            args.writer.objects['contributors.csv'].append({'ID': row['id'], 'Name': row['name']})

        cc = {
            fid: [pk2id['contributor'][r['contributor_pk']] for r in rows]
            for fid, rows in itertools.groupby(
                self.read(
                    'contributioncontributor',
                    key=lambda d: (d['contribution_pk'], d['primary'] == 'f', int(d['ord']))
                ).values(),
                lambda r: r['contribution_pk'])
        }

        areas = self.read('area')
        chapters = self.read('contribution', extended='chapter')

        for row in self.read(
                'parameter',
                extended='feature',
                pkmap=pk2id,
                key=lambda d: fid_key(d['id'])).values():
            args.writer.objects['ParameterTable'].append({
                'ID': row['id'],
                'Name': row['name'],
                'Area': areas[chapters[row['contribution_pk']]['area_pk']]['name'],
                'Chapter': chapters[row['contribution_pk']]['name'],
                'Contributor_ID': cc[row['contribution_pk']],
            })

        for row in self.read(
                'domainelement',
                pkmap=pk2id,
                key=lambda d: (fid_key(d['id'].split('-')[0]), int(d['number']))).values():
            args.writer.objects['CodeTable'].append({
                'ID': row['id'],
                'Parameter_ID': pk2id['parameter'][row['parameter_pk']],
                'Name': row['name'],
                'Description': row['description'],
                'Number': int(row['number']),
                'icon': json.loads(row['jsondata'])['icon'],
            })

        identifier = self.read('identifier')
        lang2id = collections.defaultdict(lambda: collections.defaultdict(list))
        for row in self.read('languageidentifier').values():
            id_ = identifier[row['identifier_pk']]
            lang2id[row['language_pk']][id_['type']].append((id_['name'], id_['description']))

        families = self.read('family', pkmap=pk2id)
        genera = self.read('genus', pkmap=pk2id)

        for row in self.read('language', extended='walslanguage', pkmap=pk2id).values():
            id = row['id']
            genus = genera[row['genus_pk']]
            family = families[genus['family_pk']]
            if row['name'] == genus['name'] == family['name']:
                # an isolate!
                genus = family = None
            iso_codes = set(i[0] for i in lang2id[row['pk']].get('iso639-3', []))
            glottocodes = [i[0] for i in lang2id[row['pk']].get('glottolog', [])]
            args.writer.objects['LanguageTable'].append({
                'ID': id,
                'Name': row['name'],
                'ISO639P3code': list(iso_codes)[0] if len(iso_codes) == 1 else None,
                'Glottocode': glottocodes[0] if len(glottocodes) == 1 else None,
                'ISO_codes': sorted(iso_codes),
                'Latitude': row['latitude'],
                'Longitude': row['longitude'],
                'Genus': genus['name'] if genus else None,
                'Subfamily': genus['subfamily'] if genus else None,
                'Family': family['name'] if family else None,
                'Samples_100': row['samples_100'] == 't',
                'Samples_200': row['samples_200'] == 't',
            })
        args.writer.objects['LanguageTable'].sort(key=lambda d: d['ID'])

        refs = {
            dpid: [
                str(Reference(
                    source=str(r[1]),
                    desc=r[2].replace('[', ')').replace(']', ')').replace(';', '.').strip()
                    if r[2] else None))
                for r in refs_
            ]
            for dpid, refs_ in itertools.groupby(refs, lambda r: r[0])}

        vsdict = self.read('valueset', pkmap=pk2id)

        examples = self.read('sentence', pkmap=pk2id)
        igts = {}
        for ex in examples.values():
            if all(ex[k] for k in ['description', 'analyzed', 'gloss']):
                a, g = ex['analyzed'].split(), ex['gloss'].split()
                if len(a) != len(g):
                    a, g = [ex['analyzed']], [ex['gloss']]
                igts[ex['pk']] = ex['id']
                args.writer.objects['ExampleTable'].append({
                    'ID': ex['id'],
                    'Language_ID': pk2id['language'][ex['language_pk']],
                    'Primary_Text': ex['name'],
                    'Translated_Text': ex['description'],
                    'Analyzed_Word': a,
                    'Gloss': g,
                })
        example_by_value = {
            vpk: [r['sentence_pk'] for r in rows]
            for vpk, rows in itertools.groupby(
                self.read('valuesentence', key=lambda d: d['value_pk']).values(),
                lambda d: d['value_pk']
            )
        }

        for row in self.read('value').values():
            vs = vsdict[row['valueset_pk']]
            comment = None
            ex = [examples[spk] for spk in example_by_value.get(row['pk'], [])]
            if len(ex) == 1 and not any(ex[0][k] for k in ['description', 'analyzed', 'gloss']):
                comment = ex[0]['name']
                del example_by_value[row['pk']]
            args.writer.objects['ValueTable'].append({
                'ID': vs['id'],
                'Language_ID': pk2id['language'][vs['language_pk']],
                'Parameter_ID': pk2id['parameter'][vs['parameter_pk']],
                'Value': pk2id['domainelement'][row['domainelement_pk']].split('-')[1],
                'Code_ID': pk2id['domainelement'][row['domainelement_pk']],
                'Comment': comment,
                'Source': refs.get(vs['pk'], []),
                'Example_ID': sorted(igts[epk] for epk in example_by_value.get(row['pk'], []) if epk in igts),
            })

        args.writer.objects['ValueTable'].sort(
            key=lambda d: (d['Language_ID'], fid_key(d['Parameter_ID'])))

        altnames = []
        for lpk in lang2id:
            for type in lang2id[lpk]:
                if type == 'name':
                    for name, prov in lang2id[lpk][type]:
                        altnames.append((prov, name, pk2id['language'][lpk]))

        lnid = 0
        for (type, name), rows in itertools.groupby(sorted(altnames), lambda t: (t[0], t[1])):
            lnid += 1
            args.writer.objects['language_names.csv'].append({
                'ID': str(lnid),
                'Language_ID': [r[2] for r in rows],
                'Name': name,
                'Provider': type,
            })

    def create_schema(self, cldf):
        cldf.add_component(
            'ParameterTable',
            {
                'name': 'Contributor_ID',
                'separator': ' ',
            },
            'Chapter',
            'Area',
        )
        cldf.add_component(
            'CodeTable',
            {'name': 'Number', 'datatype': 'integer'},
            'icon',
        )
        cldf.add_component(
            'LanguageTable',
            'Family',
            'Subfamily',
            'Genus',
            {
                'name': 'ISO_codes',
                'separator': ' ',
            },
            {
                'name': 'Samples_100',
                'datatype': 'boolean',
                'dc:description': "https://wals.info/chapter/s1#3.1._The_WALS_samples",
            },
            {
                'name': 'Samples_200',
                'datatype': 'boolean',
                'dc:description': "https://wals.info/chapter/s1#3.1._The_WALS_samples",
            },
        )
        cldf.add_component('ExampleTable')
        t = cldf.add_table(
            'language_names.csv',
            {
                'name': 'ID',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#id',
            },
            {
                'name': 'Language_ID',
                'separator': ' ',
            },
            {
                'name': 'Name',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#name',
            },
            'Provider',
        )
        t.common_props['dc:conformsTo'] = None
        t = cldf.add_table(
            'contributors.csv',
            {
                'name': 'ID',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#id',
            },
            {
                'name': 'Name',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#name',
            },
        )
        t.common_props['dc:conformsTo'] = None
        cldf.add_columns(
            'ValueTable',
            {
                'name': 'Example_ID',
                'separator': ' ',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#exampleReference',
            }
        )
        cldf.add_foreign_key('ParameterTable', 'Contributor_ID', 'contributors.csv', 'ID')
        cldf.add_foreign_key('language_names.csv', 'Language_ID', 'LanguageTable', 'ID')

    #
    # Raw data curation functionality:
    #
    def pk_from_id(self, thing, id_):
        if not thing.endswith('.csv'):
            thing = thing + '.csv'
        for row in self.raw_dir.read_csv(thing, dicts=True):
            if row['id'] == id_:
                return row['pk']

    def iter_rows(self, fname, cond):
        for row in self.raw_dir.read_csv(fname, dicts=True):
            if cond(row):
                yield row

    def add_rows(self, fname, *rows):
        dsv.add_rows(self.raw_dir / fname, *rows)

    def get_row(self, fname, cond):
        res = list(self.iter_rows(fname, cond))
        assert len(res) == 1
        return res[0]

    def maxpk(self, fname):
        return max(int(r['pk']) for r in self.raw_dir.read_csv(fname, dicts=True))

    def rewrite(self, fname, v):
        rows = list(dsv.reader(self.raw_dir / fname, dicts=True))

        with dsv.UnicodeWriter(self.raw_dir / fname) as w:
            for i, row in enumerate(rows):
                if i == 0:
                    w.writerow(row.keys())
                res = v(row)
                if res:
                    w.writerow(res.values())
