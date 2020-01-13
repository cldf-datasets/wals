import gzip
import pathlib
import sqlite3
import itertools

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
                    "[![Build Status](https://travis-ci.org/cldf-datasets/ewave.svg?branch=master)]"
                    "(https://travis-ci.org/cldf-datasets/ewave)"
                ])
        return '\n'.join(lines)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "wals"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_download(self, args):
        pass

    def cmd_makecldf(self, args):
        dbpath = self.raw_dir / 'wals2008.sqlite'
        with gzip.open(str(self.raw_dir / 'wals2008.sqlite.gz'), 'rb') as f:
            dbpath.write_bytes(f.read())

        gl_by_iso = {lang.iso: lang.id for lang in args.glottolog.api.languoids()}

        args.writer.cldf.add_component(
            'ParameterTable',
            {
                'name': 'Contributor_ID',
                'separator': ' ',
            },
            'Area',
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
        db = sqlite3.connect(str(dbpath))

        refs = []
        for row in db.execute('select datapoint_id, reference_id, note from datapoint_reference order by datapoint_id, reference_id, note'):
            if row[1] in sources.entries:
                refs.append((row[0], row[1], row[2]))
        srcids = set(r[1] for r in refs)
        args.writer.cldf.add_sources(
            *[Source.from_entry(id_, e) for id_, e in sources.entries.items() if id_ in srcids])

        for row in db.execute("select id, name from author order by id"):
            args.writer.objects['contributors.csv'].append({
                'ID': row[0],
                'Name': row[1],
            })

        cc = {
            fid: [r[1] for r in rows]
            for fid, rows in itertools.groupby(
                db.execute(
                    "select feature_id, author_id, `order` from feature_author order by feature_id, `order`"),
                lambda r: r[0])
        }

        for row in db.execute("""\
select
    f.id, f.name, f.area_id
from
    feature as f
order by
    cast(f.id as int)
"""):
            args.writer.objects['ParameterTable'].append({
                'ID': row[0],
                'Name': row[1],
                'Area': row[2],
                'Contributor_ID': cc[row[0]],
            })

        for row in db.execute('select numeric, feature_id, description, long_description from value order by feature_id, numeric'):
            args.writer.objects['CodeTable'].append({
                'ID': '{0}-{1}'.format(row[1], row[0]),
                'Parameter_ID': row[1],
                'Name': row[2],
                'Description': row[3],
            })

        refs = {
            dpid: [
                str(Reference(
                    source=str(r[1]),
                    desc=r[2].replace('[', ')').replace(']', ')').replace(';', '.') if r[2] else None))
                for r in refs_
            ]
            for dpid, refs_ in itertools.groupby(refs, lambda r: r[0])}

        for row in db.execute('select id, language_id, feature_id, value_numeric, source from datapoint order by language_id, feature_id'):
            args.writer.objects['ValueTable'].append({
                'ID': row[0],
                'Language_ID': row[1],
                'Parameter_ID': row[2],
                'Value': row[3],
                'Comment': row[4],
                'Source': refs.get(row[0], []),
            })
        iso = {
            lid: [r[1] for r in rows]
            for lid, rows in itertools.groupby(
                db.execute(
                    "select language_id, iso_language_id from language_iso_language order by language_id, iso_language_id"),
                lambda r: r[0])
        }

        for row in db.execute("""\
select 
    l.code, l.name, l.latitude, l.longitude, g.name, g.subfamily, f.name
from 
    language as l, genus as g, family as f
where
    l.genus_id = g.id and g.family_id = f.id
"""):
            id, name, lat, lon, genus, subfamily, family = row
            if name == genus == family:
                # an isolate!
                genus = family = None
            args.writer.objects['LanguageTable'].append({
                'ID': id,
                'Name': name,
                'ISO639P3code': iso[id][0] if len(iso.get(id, [])) == 1 else None,
                'Glottocode': gl_by_iso.get(iso[id][0]) if len(iso.get(id, [])) == 1 else None,
                'ISO_codes': iso.get(id, []),
                'Latitude': lat,
                'Longitude': lon,
                'Genus': genus,
                'Subfamily': subfamily,
                'Family': family,
            })

        for np in ['other', 'ruhlen', 'routledge']:
            for row in db.execute("""\
select
    t.name, group_concat(r.language_id, ' ')
from
    {0}name as t, {0}name_language as r
where t.name = r.{0}name_id
group by t.name""".format(np)):
                args.writer.objects['language_names.csv'].append({
                    'Language_ID': sorted(row[1].split()),
                    'Name': row[0],
                    'Provider': np,
                })
        args.writer.objects['language_names.csv'] = sorted(
            args.writer.objects['language_names.csv'],
            key=lambda d: (d['Provider'], d['Name'])
        )
        dbpath.unlink()
