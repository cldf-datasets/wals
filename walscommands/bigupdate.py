"""
Add a new language
"""
import functools
import collections

from unidecode import unidecode
import pytest
import pycountry
from cldfbench_wals import Dataset
from clldutils.misc import slug
from clldutils.color import qualitative_colors


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
    # collect new genera/families/subfamilies:
    langs = {r['pk']: r['name'] for r in ds.iter_rows('language.csv')}
    for r in ds.iter_rows('walslanguage.csv'):
        langs[r['pk']] = (langs[r['pk']], r['genus_pk'])
    genera = {r['name']: (r['pk'], r['subfamily'], r['family_pk']) for r in ds.iter_rows('genus.csv')}
    maxpk_genus = ds.maxpk('genus.csv')
    maxpk_family = ds.maxpk('family.csv')
    families = {r['name']: r['pk'] for r in ds.iter_rows('family.csv')}

    # Add new stuff
    upd_l, add_f, add_g, upd_g = {}, [], [], {}
    for lpk, d in changes.items():
        sf = None
        if 'SubfamilyNEW' in d:
            sf = d['SubfamilyNEW'][1]
        fpk = None
        if 'FamilyNEW' in d:
            oldf, newf = d['FamilyNEW']
            if newf not in families:
                maxpk_family += 1
                add_f.append([
                    # pk, jsondata, id, name, description, markup_description
                    maxpk_family, '', slug(newf), newf, '', ''])
                families[newf] = maxpk_family
            fpk = families[newf]
        if (sf is not None) or fpk or ('GenusNEW' in d):
            if 'GenusNEW' not in d:
                # Just update the family_pk or subfamily for genus!
                upd_g[langs[lpk][1]] = (sf, fpk)
                continue
            old, new = d['GenusNEW']
            # Where do we get the old familypk?
            fpk = fpk or genera[old][2]
            if not new:
                assert langs[lpk][0] == old
                continue
            if new not in genera:
                sf = sf if sf is not None else genera[old][1]
                maxpk_genus += 1
                add_g.append([
                    #pk, jsondata, id, name, description, markup_description, family_pk, subfamily, icon
                    maxpk_genus, '', slug(new), new, '', '', fpk, sf, ''])
                genera[new] = (maxpk_genus, sf, fpk)
            gpk, sf, fpk = genera[new]
            upd_l[lpk] = gpk

    ds.add_rows('family.csv', *add_f)
    ds.add_rows('genus.csv', *add_g)

    def upg(row):
        if row['pk'] in upd_g:
            sf, fpk = upd_g[row['pk']]
            if sf is not None:
                row['subfamily'] = sf
            if fpk:
                row['family_pk'] = fpk
        return row
    ds.rewrite('genus.csv', upg)

    # rewrite walslanguage.csv adapting genus_pk
    def upl(row):
        if row['pk'] in upd_l:
            row['genus_pk'] = upd_l[row['pk']]
        return row
    ds.rewrite('walslanguage.csv', upl)

    #
    # Remove
    # 1. genera no longer referenced by languages
    gpks = set(r['genus_pk'] for r in ds.iter_rows('walslanguage.csv'))
    ds.rewrite('genus.csv', lambda r: r if r['pk'] in gpks else None)

    # 2. families no longer referenced by genera
    fpks = set(r['family_pk'] for r in ds.iter_rows('genus.csv'))
    ds.rewrite('family.csv', lambda r: r if r['pk'] in fpks else None)

    # Reassign genus icons.
    ngenus = len(list(ds.iter_rows('genus.csv')))
    colors = qualitative_colors(ngenus)

    def assign_icon(row):
        row['icon'] = colors.pop().replace('#', 'c')
        return row
    ds.rewrite('genus.csv', assign_icon)

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
    update = {row['ID']: row for row in ds.raw_dir.read_csv('languagesMSD_22-09.csv', dicts=True)}
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
            if lid not in update:
                continue
            for okey, nkey, conv in CMP[table + '.csv']:
                old, new = conv(lang[okey], genera, idsBylpk, countriesBylpk), conv(update[lid][nkey], genera, idsBylpk, countriesBylpk)
                if (pytest.approx(old) if isinstance(old, float) else old) != (pytest.approx(new) if isinstance(new, float) else new):
                    changes[lang['pk']][nkey] = (old, new)
                    if args.dryrun:
                        print('new ({}, {}): {}: {} -> {}'.format(okey, nkey, lid, old, new))
    if not args.dryrun:
        change(ds, changes)
