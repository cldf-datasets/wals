import re
import pathlib
import itertools

from cldfbench import Dataset as BaseDataset
from cldfbench import CLDFSpec, Metadata
from pycldf.sources import Source, Reference
from pybtex.database import parse_string

"""
altname.csv
	altname_language.csv
	area.csv
	author.csv
	author_chapter.csv
	author_supplement.csv
	chapter.csv
	chapter_olacsubject.csv
	chapter_reference.csv
	country.csv
	country_language.csv
	datapoint.csv
	datapoint_reference.csv
	example.csv
	example_feature.csv
	example_reference.csv
	family.csv
	feature.csv
	genus.csv
	igt.csv
	isolanguage.csv
	isolanguage_language.csv
	language.csv
	olacsubject.csv
	reference.csv
	reference_supplement.csv
	rmmodified.py
	supplement.csv
	tocsv.sh
	value.csv
"""


class MetadataWithTravis(Metadata):
    def markdown(self):
        lines, title_found = [], False
        for line in super().markdown().split('\n'):
            lines.append(line)
            if line.startswith('# ') and not title_found:
                title_found = True
                lines.extend([
                    '',
                    "[![Build Status](https://travis-ci.org/cldf-datasets/ewave.svg?branch=master)]"
                    "(https://travis-ci.org/cldf-datasets/ewave)"
                ])
        return '\n'.join(lines)


def fid_key(fid):
    i = re.search('[A-Z]', fid).start()
    return (int(fid[:i]), fid[i:])


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "wals"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):
        pass

    def cmd_makecldf(self, args):
        gl_by_iso = {lang.iso: lang.id for lang in args.glottolog.api.languoids()}

        args.writer.cldf.add_component(
            'ParameterTable',
            {
                'name': 'Contributor_ID',
                'separator': ' ',
            },
            'Area',
            'Chapter',
        )
        args.writer.cldf.add_component('CodeTable')
        args.writer.cldf.add_component(
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
        args.writer.cldf.add_table(
            'language_names.csv',
            {
                'name': 'Language_ID',
                'separator': ' ',
            },
            'Name',
            'Provider',
        )
        args.writer.cldf.add_table(
            'contributors.csv',
            'ID',
            'Name',
        )
        args.writer.cldf.add_foreign_key(
            'ParameterTable', 'Contributor_ID', 'contributors.csv', 'ID')
        args.writer.cldf.add_foreign_key(
            'language_names.csv', 'Language_ID', 'LanguageTable', 'ID')

        sources = parse_string(
            self.raw_dir.joinpath('source.bib').read_text(encoding='utf8'), 'bibtex')

        refs = []
        for row in self.raw_dir.read_csv('datapoint_reference.csv', dicts=True):
            if row['reference_id'] in sources.entries:
                refs.append(list(row.values()))
        srcids = set(r[1] for r in refs)
        args.writer.cldf.add_sources(
            *[Source.from_entry(id_, e) for id_, e in sources.entries.items() if id_ in srcids])

        for row in sorted(self.raw_dir.read_csv('author.csv', dicts=True), key=lambda r: r['id']):
            args.writer.objects['contributors.csv'].append({'ID': row['id'], 'Name': row['name']})

        cc = {
            fid: [r['author_id'] for r in rows]
            for fid, rows in itertools.groupby(
                self.raw_dir.read_csv('author_chapter.csv', dicts=True),
                lambda r: r['chapter_id'])
        }
        area = {r['id']: r['name'] for r in self.raw_dir.read_csv('area.csv', dicts=True)}
        chapter = {
            r['id']: (r['name'], area[r['area_id']])
            for r in self.raw_dir.read_csv('chapter.csv', dicts=True)}

        for row in sorted(self.raw_dir.read_csv('feature.csv', dicts=True), key=lambda d: fid_key(d['id'])):
            a, c = chapter[row['chapter_id']]
            args.writer.objects['ParameterTable'].append({
                'ID': row['id'],
                'Name': row['name'],
                'Area': a,
                'Chapter': c,
                'Contributor_ID': cc[row['chapter_id']],
            })

        for row in sorted(self.raw_dir.read_csv('value.csv', dicts=True), key=lambda d: (fid_key(d['feature_id']), int(d['numeric']))):
            args.writer.objects['CodeTable'].append({
                'ID': '{0}-{1}'.format(row['feature_id'], row['numeric']),
                'Parameter_ID': row['feature_id'],
                'Name': row['description'],
                'Description': row['long_description'],
            })

        refs = {
            dpid: [
                str(Reference(
                    source=str(r[1]),
                    desc=r[2].replace('[', ')').replace(']', ')').replace(';', '.') if r[2] else None))
                for r in refs_
            ]
            for dpid, refs_ in itertools.groupby(refs, lambda r: r[0])}

        for row in sorted(self.raw_dir.read_csv('datapoint.csv', dicts=True), key=lambda d: (d['language_id'], fid_key(d['feature_id']))):
            args.writer.objects['ValueTable'].append({
                'ID': row['id'],
                'Language_ID': row['language_id'],
                'Parameter_ID': row['feature_id'],
                'Value': row['value_numeric'],
                'Code_ID': '{0}-{1}'.format(row['feature_id'], row['value_numeric']),
                'Comment': row['source'],
                'Source': refs.get(row['id'], []),
            })
        iso = {
            lid: [r['isolanguage_id'] for r in rows]
            for lid, rows in itertools.groupby(
                sorted(self.raw_dir.read_csv('isolanguage_language.csv', dicts=True), key=lambda d: tuple(d.values())),
                lambda r: r['language_id'])
        }
        family = {
            r['id']: r['name']
            for r in self.raw_dir.read_csv('family.csv', dicts=True)
        }
        genus = {
            r['id']: (r['name'], r['subfamily'], family[r['family_id']])
            for r in self.raw_dir.read_csv('genus.csv', dicts=True)
        }

        for row in sorted(self.raw_dir.read_csv('language.csv', dicts=True), key=lambda d: d['id']):
            id = row['id']
            genus_, subfamily, family = genus[row['genus_id']]
            if row['name'] == genus_ == family:
                # an isolate!
                genus_ = family = None
            args.writer.objects['LanguageTable'].append({
                'ID': id,
                'Name': row['name'],
                'ISO639P3code': iso[id][0] if len(iso.get(id, [])) == 1 else None,
                'Glottocode': gl_by_iso.get(iso[id][0]) if len(iso.get(id, [])) == 1 else None,
                'ISO_codes': iso.get(id, []),
                'Latitude': row['latitude'],
                'Longitude': row['longitude'],
                'Genus': genus_,
                'Subfamily': subfamily,
                'Family': family,
                'Samples_100': row['samples_100'] == 't',
                'Samples_200': row['samples_200'] == 't',
            })

        for (type, name), rows in itertools.groupby(
            sorted(
                self.raw_dir.read_csv('altname_language.csv', dicts=True),
                key=lambda d: (d['altname_type'], d['altname_name'], d['language_id'])),
            lambda d: (d['altname_type'], d['altname_name'])
        ):
            args.writer.objects['language_names.csv'].append({
                'Language_ID': [r['language_id'] for r in rows],
                'Name': name,
                'Provider': type,
            })
