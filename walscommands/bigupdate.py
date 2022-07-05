"""
Add a new language
"""
import functools
import collections

from unidecode import unidecode
import pytest
import pycountry
from cldfbench_wals import Dataset


CMP = {
    'language.csv': [
        ('name', 'NameNEW', lambda s, *args: s),  # edit language.name + walslanguage.ascii_name
        ('latitude', 'LatitudeNEW', lambda s, *args: float(s)),  # edit language.latitude
        ('longitude', 'LongitudeNEW', lambda s, *args: float(s)),  # edit language.longitude
    ],
    'walslanguage.csv': [
        ('macroarea', 'MacroareaNEW', lambda s, *args: s),  # edit walslanguage.macroarea
        ('iso_codes', 'ISO_codesNEW', lambda s, *args: s.replace(',', '')),  # edit walslanguage.iso_codes
        ('pk', 'GlottocodeNEW', lambda s, g, ids, *args: ids.get(s, Identifiers()).glottocode if s.isnumeric() else s),
        ('pk', 'Country_IDNEW', lambda s, g, i, c, *args: c.get(s, Countries()).id if s.isnumeric() else s),

        #
        # FIXME: todo
        #
        ('genus_pk', 'GenusNEW', lambda s, genera, *args: genera[s][0] if s in genera else s),
        ('genus_pk', 'SubfamilyNEW', lambda s, genera, *args: genera[s][2] if s in genera else s),
        ('genus_pk', 'FamilyNEW', lambda s, genera, *args: genera[s][1] if s in genera else s),
    ]
}


class Identifiers(list):
    @property
    def glottocode(self):
        for i in self:
            if i['type'] == 'glottolog':
                return i['name']
        return ''


class Countries(list):
    @property
    def id(self):
        return ' '.join(self)


def change(ds, changes):
    glottocodes = {
        row['name']: row['pk'] for row in ds.iter_rows(
            'identifier.csv', lambda r: r['type'] == 'glottolog')}
    maxpk_identifier = ds.maxpk('identifier.csv')
    maxpk_languageidentifier = ds.maxpk('languageidentifier.csv')
    rem_li, add_li, add_i = set(), [], []

    countries = {row['id']: row['pk'] for row in ds.iter_rows('country.csv')}
    maxpk_country = ds.maxpk('country.csv')
    maxpk_countrylanguage = ds.maxpk('countrylanguage.csv')
    rem_lc, add_lc, add_c = set(), [], []
    # Now figure out which ones to keep and which to add:
    for lpk, d in changes.items():
        if 'GlottocodeNEW' in d:
            old, new = d['GlottocodeNEW']
            if old:
                # remove reference:
                rem_li.add((lpk, glottocodes[old]))

            if new:
                if new not in glottocodes:
                    maxpk_identifier += 1
                    add_i.append([
                        #pk, jsondata, name, description, markup_description, id,type,lang,version
                        maxpk_identifier, '', new, '', '', 'gc-' + new, 'glottolog', 'en', 1])
                    glottocodes[new] = maxpk_identifier
                # add reference:
                maxpk_languageidentifier += 1
                add_li.append([
                    # pk, jsondata, language_pk, identifier_pk, description, version
                    maxpk_languageidentifier, '', lpk, glottocodes[new], '', 1])
        if 'Country_IDNEW' in d:
            old, new = d['Country_IDNEW']
            old = old.split()
            new = new.split()
            for o in set(old) - set(new):
                rem_lc.add((lpk, countries[o]))
            for n in set(new) - set(old):
                if n not in countries:
                    c = pycountry.countries.get(alpha_2=n)
                    maxpk_country += 1
                    add_c.append([
                        #pk, jsondata, id, name, description, markup_description, continent
                        maxpk_country, '', n, c.name, '', '', ''])
                    countries[n] = maxpk_country
                maxpk_countrylanguage += 1
                add_lc.append([
                    #pk, jsondata, country_pk, language_pk
                    maxpk_countrylanguage, '', countries[n], lpk])
    ds.rewrite(
        'languageidentifier.csv',
        lambda r: None if (r['language_pk'], r['identifier_pk']) in rem_li else r)
    ds.add_rows('identifier.csv', *add_i)
    ds.add_rows('languageidentifier.csv', *add_li)
    ds.rewrite(
        'countrylanguage.csv',
        lambda r: None if (r['language_pk'], r['country_pk']) in rem_lc else r)
    ds.add_rows('country.csv', *add_c)
    ds.add_rows('countrylanguage.csv', *add_lc)

    def changer(table, row):
        for i, (k, (old, new)) in enumerate(changes.get(row['pk'], {}).items()):
            if table == 'language':
                if k == 'NameNEW':
                    row['name'] = new
                elif k == 'LatitudeNEW':
                    row['latitude'] = new
                elif k == 'LongitudeNEW':
                    row['longitude'] = new
            elif table == 'walslanguage':
                if k == 'Name_NEW':
                    row['ascii_name'] = unidecode(new)
                elif k == 'MacroareaNEW':
                    row['macroarea'] = new
                elif k == 'ISO_codesNEW':
                    row['iso_codes'] = ', '.join(new.split())
        return row

    ds.rewrite('language.csv', functools.partial(changer, 'language'))
    ds.rewrite('walslanguage.csv', functools.partial(changer, 'walslanguage'))


def register(parser):
    parser.add_argument('--dryrun', action='store_true', default=False)


def run(args):
    changes = collections.defaultdict(dict)
    ds = Dataset()
    update = {row['ID']: row for row in ds.raw_dir.read_csv('languagesMSD.csv', dicts=True)}
    families = {row['pk']: row['name'] for row in ds.iter_rows('family.csv')}
    genera = {row['pk']: (row['name'], families[row['family_pk']], row['subfamily']) for row in ds.iter_rows('genus.csv')}
    ids = {row['pk']: row for row in ds.iter_rows('identifier.csv')}
    idsBylpk = collections.defaultdict(Identifiers)
    for row in ds.iter_rows('languageidentifier.csv'):
        idsBylpk[row['language_pk']].append(ids[row['identifier_pk']])
    countries = {row['pk']: row['id'] for row in ds.iter_rows('country.csv')}
    countriesBylpk = collections.defaultdict(Countries)
    for row in ds.iter_rows('countrylanguage.csv'):
        countriesBylpk[row['language_pk']].append(countries[row['country_pk']])

    pk2id = {}
    for table in ['language', 'walslanguage']:
        for lang in ds.iter_rows(table + '.csv', lambda i: True):
            if table == 'language':
                pk2id[lang['pk']] = lang['id']
                lid = lang['id']
            else:
                lid = pk2id[lang['pk']]
            for okey, nkey, conv in CMP[table + '.csv']:
                old, new = conv(lang[okey], genera, idsBylpk, countriesBylpk), conv(update[lid][nkey], genera, idsBylpk, countriesBylpk)
                if (pytest.approx(old) if isinstance(old, float) else old) != (pytest.approx(new) if isinstance(new, float) else new):
                    changes[lang['pk']][nkey] = (old, new)
                    if args.dryrun:
                        print('new ({}, {}): {}: {} -> {}'.format(okey, nkey, lid, old, new))
    if not args.dryrun:
        change(ds, changes)
