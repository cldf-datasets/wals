import io
import re
import json
import pathlib
import itertools
import collections

from csvw import dsv
from csvw.metadata import URITemplate
from cldfbench import Dataset as BaseDataset
from cldfbench import CLDFSpec
from clldutils.misc import data_url, slug
from clldutils.color import qualitative_colors
from pycldf.sources import Source, Reference
from pybtex.database import parse_string
from newick import Node
import nexus
from nexus.handlers.tree import Tree as NexusTree


def fid_key(fid):
    i = re.search('[A-Z]', fid).start()
    return (int(fid[:i]), fid[i:])


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "wals"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(
            module='StructureDataset',
            data_fnames={
                'ContributionTable': 'chapters.csv',
                'TreeTable': 'genealogy.csv',
            },
            dir=self.cldf_dir)

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
        glangs = {l.id for l in args.glottolog.api.languoids()}

        pk2id = collections.defaultdict(dict)

        skip_source = [
            'Lous-1969',  # -> Loos-1969
            'Payne-1990',  # -> Payne-1990a
        ]
        updated_source_keys = {
            'Anonymous-nd': 'North-East-Frontier-Agency-1963',
        }
        updated_source_names = {
            'North-East-Frontier-Agency-1963': 'North East Frontier Agency 1963',
        }
        sources = parse_string(
            self.raw_dir.joinpath('source.bib').read_text(encoding='utf8'), 'bibtex')
        gbs_lg_refs = collections.defaultdict(set)
        src_names = {}
        for s in self.read('source', pkmap=pk2id).values():
            if s['id'] in skip_source:
                continue
            s['id'] = updated_source_keys.get(s['id'], s['id'])
            src_names[s['id']] = updated_source_names.get(s['id'], s['name'])
            try:
                jsd = json.loads(s['jsondata'])
                if 'wals_code' in jsd:
                    [gbs_lg_refs[c].add(s['id']) for c in jsd['wals_code']]
                gbs = jsd['gbs']
                if gbs['id'].strip():
                    sef = sources.entries[s['id']].fields
                    sef['google_book_search_id'] = gbs['id'].strip()
                    sef['google_book_viewability'] = gbs['accessInfo']['viewability'].strip()
            except (json.decoder.JSONDecodeError, KeyError):
                continue

        chapters = self.read('contribution', extended='chapter', pkmap=pk2id)

        refs = []
        crefs = collections.defaultdict(list)
        for row in self.raw_dir.read_csv('valuesetreference.csv', dicts=True):
            if row['source_pk']:
                sid = pk2id['source'][row['source_pk']]
                if sid not in skip_source:
                    refs.append((row['valueset_pk'], updated_source_keys.get(sid, sid), row['description']))
        srcids = set(r[1] for r in refs)
        for row in self.raw_dir.read_csv('contributionreference.csv', dicts=True):
            sid = pk2id['source'][row['source_pk']]
            if sid not in crefs[pk2id['contribution'][row['contribution_pk']]]:
                crefs[pk2id['contribution'][row['contribution_pk']]].append(sid)
                srcids.add(sid)
        unused_srcids = []
        for id_, e in sources.entries.items():
            if id_ in skip_source:
                continue
            if id_ in srcids:
                if id_ in src_names:
                    e.fields['wals_ref_name'] = src_names[id_]
                args.writer.cldf.add_sources(Source.from_entry(id_, e))
            else:
                unused_srcids.append(id_)
            # add language references out of bibtex tag 'wals_code'
            # to ensure that nothing was missed in raw/languagesource.csv (37 cases)
            if 'wals_code' in e.fields:
                [gbs_lg_refs[c].add(id_) for c in e.fields['wals_code'].split('; ')]

        for id_, e in sources.entries.items():
            if id_ in skip_source:
                continue
            if id_ in unused_srcids:
                if id_ in src_names:
                    e.fields['wals_ref_name'] = src_names[id_]
                args.writer.cldf.add_sources(Source.from_entry(id_, e))

        editors = {e['contributor_pk']: int(e['ord']) for e in self.read(
                    'editor', key=lambda r: int(r['ord'])).values()}

        contributors = self.read('contributor', pkmap=pk2id, key=lambda r: r['id'])
        for row in contributors.values():
            args.writer.objects['contributors.csv'].append({
                'ID': row['id'],
                'Name': row['name'],
                'Url': row['url'],
                'Editor_Ord': editors[row['pk']] if row['pk'] in editors else 0,
            })
        contributors = {d['ID']: d['Name'] for d in args.writer.objects['contributors.csv']}

        cc = {
            chapters[fid]['id']: [(r['primary'], pk2id['contributor'][r['contributor_pk']]) for r in rows]
            for fid, rows in itertools.groupby(
                self.read(
                    'contributioncontributor',
                    key=lambda d: (d['contribution_pk'], d['primary'] == 'f', int(d['ord']))
                ).values(),
                lambda r: r['contribution_pk'])
        }

        areas = self.read('area')
        for row in areas.values():
            args.writer.objects['areas.csv'].append({
                'ID': row['id'],
                'Name': row['name'],
                'dbpedia_url': row['dbpedia_url'],
            })

        for row in self.read(
                'parameter',
                extended='feature',
                pkmap=pk2id,
                key=lambda d: fid_key(d['id'])).values():
            args.writer.objects['ParameterTable'].append({
                'ID': row['id'],
                'Name': row['name'],
                'Chapter_ID': chapters[row['contribution_pk']]['id'],
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
        countries = self.read('country', pkmap=pk2id)
        lang2country = collections.defaultdict(list)
        for c in self.read('countrylanguage').values():
            lang2country[c['language_pk']].append(pk2id['country'][c['country_pk']])
        lrefs = collections.defaultdict(list)
        for c in self.read('languagesource').values():
            sid = pk2id['source'][c['source_pk']]
            sid = updated_source_keys.get(sid, sid)
            if sid not in lrefs[c['language_pk']]:
                lrefs[c['language_pk']].append(sid)

        ngenus = collections.Counter()
        for row in self.read('language', extended='walslanguage', pkmap=pk2id).values():
            id = row['id']
            genus = genera[row['genus_pk']]
            ngenus.update([genus['name']])
            family = families[genus['family_pk']]
            iso_codes = row['iso_codes'].replace(',', '').split()
            glottocodes = [i[0] for i in lang2id[row['pk']].get('glottolog', [])]
            gcode = glottocodes[0] if len(glottocodes) == 1 else None
            if gcode:
                assert gcode in glangs, 'invalid Glottocode: {}'.format(gcode)
            srcs = lrefs[row['pk']]
            if id in gbs_lg_refs:
                [srcs.append(s) for s in gbs_lg_refs[id] if s not in srcs]
            args.writer.objects['LanguageTable'].append({
                'ID': id,
                'Name': row['name'].strip(),
                'ISO639P3code': list(iso_codes)[0] if len(iso_codes) == 1 else None,
                'Glottocode': glottocodes[0] if len(glottocodes) == 1 else None,
                'ISO_codes': sorted(iso_codes),
                'Latitude': row['latitude'],
                'Longitude': row['longitude'],
                'Macroarea': row['macroarea'],
                'Genus': genus['name'],
                'GenusIcon': None,
                'Subfamily': genus['subfamily'] if genus else None,
                'Family': family['name'],
                'Samples_100': row['samples_100'] == 't',
                'Samples_200': row['samples_200'] == 't',
                'Country_ID': lang2country[row['pk']],
                'Source': sorted(srcs),
                'Parent_ID': None,
            })
        args.writer.objects['LanguageTable'].sort(key=lambda d: d['ID'])
        icons = dict(zip([g[0] for g in ngenus.most_common()], qualitative_colors(len(ngenus))))

        nex = nexus.NexusWriter()
        subgroups = []
        for f, lgs in itertools.groupby(
            sorted(
                args.writer.objects['LanguageTable'],
                key=lambda d: (d['Family'] or '', d['Subfamily'] or '', d['Genus'] or '', d['ID'])),
            lambda l: l['Family'],
        ):
            fid = 'family-{}'.format(slug(f))
            fn = Node(fid)
            subgroups.append(dict(ID=fid, Name=f))
            for sf, llgs in itertools.groupby(lgs, lambda l: l['Subfamily']):
                sfid = None
                if sf:
                    sfid = 'subfamily-{}'.format(slug(sf))
                    sfn = Node(sfid)
                    fn.add_descendant(sfn)
                    subgroups.append(dict(ID=sfid, Name=sf, Parent_ID=fid))

                for g, lllgs in itertools.groupby(llgs, lambda l: l['Genus']):
                    gid = 'genus-{}'.format(slug(g))
                    gn = Node(gid)
                    subgroups.append(dict(
                        ID=gid,
                        Name=g,
                        GenusIcon=icons[g].replace('#', 'c'),
                        Parent_ID=sfid if sf else fid))
                    if sf:
                        sfn.add_descendant(gn)
                    else:
                        fn.add_descendant(gn)
                    for lg in lllgs:
                        gn.add_descendant(Node(lg['ID']))
                        lg['Parent_ID'] = gid

            args.writer.objects['TreeTable'].append(dict(
                ID=fid,
                Name=fid,
                Description='Genealogical classification of the languages in the family {}'.format(f),
                Media_ID='genealogy',
            ))
            nex.trees.append(NexusTree.from_newick(fn, name=fid, rooted=True))
        args.writer.objects['LanguageTable'].extend(subgroups)
        nex.write_to_file(args.writer.cldf_spec.dir / 'genealogy.nex')
        args.writer.objects['MediaTable'].append(dict(
            ID='genealogy',
            Media_Type='text/plain',
            Download_URL='genealogy.nex',
            Contribution_ID='s4',
        ))

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
                    'Analyzed_Word': ['…' if t is None else t for t in a],
                    'Gloss': ['…' if t is None else t for t in g],
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
                comment = re.sub(r'[\r\n]', '', ex[0]['xhtml'])
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
                'Name': name.strip(),
                'Provider': type,
            })

        for c in sorted(countries.values(), key=lambda x: x['id']):
            args.writer.objects['countries.csv'].append({
                'ID': c['id'],
                'Name': c['name'],
            })

        desc_dir = self.raw_dir / 'descriptions'
        src_pattern = re.compile(
            'src="https?://wals.info/static/descriptions/(?P<sid>s?[0-9]+)/images/(?P<fname>[^"]+)"')

        def repl(m):
            p = desc_dir.joinpath(m.group('sid'), 'images', m.group('fname'))
            if p.exists():
                return 'src="{0}"'.format(data_url(p))
            return m.string[m.start():m.end()]

        descs = {}
        docs_dir = self.cldf_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)
        for d in desc_dir.iterdir():
            if d.is_dir():
                if d.joinpath('body.xhtml').exists():
                    descs[d.stem] = (src_pattern.sub(
                        repl, d.joinpath('body.xhtml').read_text(encoding='utf8')), 'html')
                else:
                    descs[d.stem] = (d.joinpath('body.md').read_text(encoding='utf8'), 'md')

        def with_citation(d):
            wals = self.metadata.citation
            authors = ', '.join(contributors[cid] for cid in d['Contributor_ID'])
            if d['With_Contributor_ID']:
                authors += ' ({})'.format(', '.join(contributors[cid] for cid in d['With_Contributor_ID']))
            d['Contributor'] = authors
            d['Citation'] = "{}. 2013. {}. In: {}".format(
                authors,
                d['Name'],
                wals.replace('https://wals.info', 'https://wals.info/chapter/{}'.format(d['Number'])))
            return d

        for c in sorted(chapters.values(), key=lambda x: int(x['sortkey'])):
            fname = docs_dir / 'chapter_{}.{}'.format(c['id'], descs[c['id']][1])
            with io.open(fname, 'w', encoding='utf-8') as f:
                f.write(descs[c['id']][0])
            cid, wcid = [], []
            if c['id'] in cc:
                cid = [co[1] for co in cc[c['id']] if co[0] == 't']
                wcid = [co[1] for co in cc[c['id']] if co[0] == 'f']
            args.writer.objects['MediaTable'].append(dict(
                ID=c['id'],
                Media_Type="text/html" if fname.suffix == 'html' else 'text/markdown',
                Conforms_To='CLDF Markdown' if fname.suffix == '.md' else None,
                Download_URL='file:///docs/{}'.format(fname.name),
                Contribution_ID=c['id'],
            ))
            args.writer.objects['ContributionTable'].append(with_citation({
                'ID': c['id'],
                'Name': c['name'],
                'wp_slug': c['wp_slug'],
                'Number': c['sortkey'],
                'Area_ID': areas[c['area_pk']]['id'] if c['area_pk'] in areas else '',
                'Source': crefs.get(c['id'], []),
                'Contributor_ID': cid,
                'With_Contributor_ID': wcid,
            }))

    def create_schema(self, cldf):
        t = cldf.add_component(
            'ParameterTable',
            'Chapter_ID',
        )
        t.common_props['dc:description'] = "WALS' Features"
        cldf.add_component(
            'CodeTable',
            {'name': 'Number', 'datatype': 'integer'},
            'icon',
        )
        t = cldf.add_component(
            'LanguageTable',
            'Family',
            'Subfamily',
            'Genus',
            'GenusIcon',
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
            {
                'name': 'Country_ID',
                'separator': ' ',
            },
            {
                'name': 'Source',
                'separator': ' '
            },
            {
                "name": "Parent_ID",
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#languageReference',
            }
        )
        t.common_props['dc:description'] = \
            "WALS' languages and language groups. WALS languages have 2 or 3 letter IDs, whereas " \
            "the taxonomic units of the  Genealogical Language List have IDs prefixed with " \
            "'family-', 'subfamily-' or 'genus-'."
        cldf.add_component('ExampleTable')
        cldf[('ExampleTable', 'Gloss')].null = ['_____']
        cldf[('ExampleTable', 'Analyzed_Word')].null = ['_____']
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
        t = cldf.add_table(
            'countries.csv',
            {
                'name': 'ID',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#id',
            },
            {
                'name': 'Name',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#name',
            },
        )
        t = cldf.add_component(
            'MediaTable',
            {
                'name': 'Contribution_ID',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#contributionReference',
            },
            {
                'name': 'Conforms_To',
                'propertyUrl': 'http://purl.org/dc/terms/conformsTo',
            },
        )
        t.common_props['dc:description'] = "Media files associated with WALS chapters."
        cldf['TreeTable'].common_props['dc:description'] = \
            "The family trees of WALS' Genealogical Language List."
        cldf.add_columns(
            'ContributionTable',
            'wp_slug',
            {
                'name': 'Number',
                'datatype': 'integer'
            },
            'Area_ID',
            {
                'name': 'Source',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#source',
                'separator': ' '
            },
            {
                'name': 'Contributor_ID',
                'separator': ' ',
            },
            {
                'name': 'With_Contributor_ID',
                'separator': ' ',
            },
        )
        cldf[('ContributionTable', 'ID')].valueUrl = URITemplate('docs/chapter_{ID}.html')
        t = cldf.add_table(
            'areas.csv',
            {
                'name': 'ID',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#id',
                'valueUrl': 'docs/chapter_{ID}.html',
            },
            {
                'name': 'Name',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#name',
            },
            {
                'name': 'dbpedia_url',
            },
        )
        t.common_props['dc:description'] = 'Linguistic Subfields'
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
            {
                'name': 'Url',
            },
            {
                'name': 'Editor_Ord',
                'datatype': 'integer',
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
        cldf.__getitem__(('ValueTable', 'Comment')).common_props['dc:description'] = 'comments in HTML'
        cldf.__getitem__(('ValueTable', 'Comment')).common_props['dc:format'] = 'text/html'
        cldf.add_foreign_key('ContributionTable', 'Contributor_ID', 'contributors.csv', 'ID')
        cldf.add_foreign_key('ContributionTable', 'With_Contributor_ID', 'contributors.csv', 'ID')
        cldf.add_foreign_key('ParameterTable', 'Chapter_ID', 'ContributionTable', 'ID')
        cldf.add_foreign_key('ContributionTable', 'Area_ID', 'areas.csv', 'ID')
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

    def iter_rows(self, fname, cond=None):
        for row in self.raw_dir.read_csv(fname, dicts=True):
            if (cond is None) or cond(row):
                yield row

    def add_rows(self, fname, *rows):
        dsv.add_rows(self.raw_dir / fname, *rows)

    def get_row(self, fname, cond):
        res = list(self.iter_rows(fname, cond))
        assert len(res) == 1
        return res[0]

    def maxpk(self, fname):
        return max(int(r['pk']) for r in self.raw_dir.read_csv(fname, dicts=True))

    def rewrite(self, fname, v, cascade=None):
        rows = list(dsv.reader(self.raw_dir / fname, dicts=True))
        pks = set()

        with dsv.UnicodeWriter(self.raw_dir / fname) as w:
            for i, row in enumerate(rows):
                if i == 0:
                    w.writerow(row.keys())
                res = v(row)
                if res:
                    w.writerow(res.values())
                    pks.add(res['pk'])

        for fn, fk in (cascade or []):
            self.rewrite(fn, lambda r: r if r[fk] in pks else None)

        return max([int(pk) for pk in pks])
