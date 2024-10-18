# Changelog

Changes between releases of the WALS CLDF dataset.


## [v2020.4] - 2024-10-18

- Fixed errata in language metadata.
- Updated Glottocodes to match Glottolog 5.0.
- For a full list of changes run `git diff v2020.3 v2020.4 cldf` on the repository.


## [v2020.3] - 2022-12-01

- Changes to language metadata as specified in `raw/languagesMSD_22-09.csv`.
- The trees of the Genealogical Language List have been added in a TreeTable.
- Chapters are now listed in a proper CLDF ContributionTable, including
  citations and link to the description.


## [v2020.2] - 2022-07-07

Changes to language metadata as specified in `raw/languagesMSD.csv`.

See also
https://github.com/cldf-datasets/wals/milestone/1?closed=1


## [v2020.1] - 2021-04-13

Fleshed out the CLDF data to contain everything that's needed to feed
https://wals.info.

See
https://github.com/cldf-datasets/wals/compare/v2020...v2020.1
for details.

## [v2020] - 2020-03-27

Minor corrections.

See https://github.com/cldf-datasets/wals/milestone/2?closed=1
for a list of addressed issues.


## [v2014]

Three value assignments have been corrected and small corrections have been made to the classification mainly triggered by updates in Glottolog's classification.


## [v2013]

Several datapoints have been removed (typically because they had been assigned to the wrong language, thus they show up as additions above).


## [v2011]

- There are two new chapters (chapter 143 on Order of Negative Morpheme and Verb, and chapter 144 on Position of Negative Word With Respect to Subject, Object, and Verb, both with many new maps)
- Additional features have been added to some chapters.
- The genealogical classification of languages, including genera, has been updated.
- The one-to-many relationship between chapters and features/maps is now clearly reflected in the structure of WALS: A single chapter can contain not just one feature, but several features, most often two (e.g. feature 39A and feature 39B), but sometimes (with the new chapters 143 and 144) quite a few features and maps.
- For some of the features, WALS now includes examples supplied by the authors (for example feature 113A)
- WALS Online now contains the long introduction chapter of the printed atlas from 2005


## [v2008]

The following errata in the printed edition of WALS have been corrected in WALS Online from 2008:

### Value assignment errors (29)

- Ch. 18: Oneida 5 -> 2
- Ch. 33:
  - Basque 2 -> 8 (plural clitic)
  - Yagaria 2 -> 8
- Ch. 33: Tshangla 2 -> 8 (Plural clitic) (Andvik 1999: 123)
- Ch. 36: Mauritian Creole 3 -> 1 (check!)
- Ch. 37:
  - Alamblak 2 -> 1
  - Tajik 1 -> 4 (No definite, but indefinite article)
- Ch. 38: Swedish 1 -> 2 (Indefinite word same as ‘one’)
- Ch. 51: Tshangla 1 -> 6 (Postpositional clitic) (Andvik 1999: 123)
- Ch. 57: Yagaria 2 -> 3
- Ch. 71: Kawaiisu 2 -> 4
- Ch. 81: Sobei 7 -> 2 (SVO)
- Ch. 83: Sobei 3 -> 2 (VO)
- Ch. 86: Fongbe 1 -> 2 (Noun-genitive)
- Ch. 86: Arop-Lokep 1 -> 3 (No dominant order)
- Ch. 87: Mussau 3 -> 1 (Adjective-noun)
- Ch. 88:
  - Breton 4 -> 2 (Noun-demonstrative)
  - Erromangan 1 -> 2 (Noun-demonstrative)
  - Qiang 1 -> 2
  - Yagaria 1 -> 6
- Ch. 89: Hanga Hundi 1 -> 3 (No dominant order)
- Ch. 90:
  - Garo 1 -> 2 (Relative clause-noun)
  - Lisu 7 -> 2 (Relative clause-noun)
- Ch. 92: Kele 6 -> 2 (Final)
- Ch. 96: Garo 2 -> 1
- Ch. 96: Lisu 5 -> 1
- Ch. 97: Mussau 5 -> 3
- Ch. 116:
  - Kele 6 -> 1 (Question particle)
  - Yagaria 2 -> 1

### Language identification errors

Ch. 74: Gadaba should be “Gadaba (Kondekor)” (this is a
language which so far has not been on the list of WALS
languages) (WALS code: gdk)

- WALS language “Mekens” (WALS code: mek)
  Ethnologue (14th ed.): SKF Sakirabiá
  Ethnologue (15th ed.): skf Sakirabiá
- WALS language “Malagasy” (WALS code: mal)
  Ethnologue (15th ed.): plt Malagasy, Plateau
- WALS language “Chaga” (WALS code: cga)
  Ethnologue (15th ed.): old Mochi
- WALS language “Kana” (WALS code: kan)
  Ethnologue (15th ed.): ogo Khana
- WALS language “Kinga” (WALS code: kga)
  Ethnologue (15th ed.): zga Kinga
- WALS language “Yi” (WALS code: yi)
  Ethnologue (15th ed.): iii Yi, Sichuan
- WALS language “Anguthimri” (WALS code: agt)
  Ethnologue (15th ed.): lnj Leningitij
- WALS language “Marchha” (WALS code: mrc)
  Ethnologue (15th ed.): rnp Rongpo
- WALS language “Warrwa” (WALS code: wrw)
  Ethnologue (15th ed.): wwr Warrwa
- WALS language “Eudeve” (WALS code: eud)
  Ethnologue (15th ed.): opt Opata
- WALS language “Lalo” (WALS code: lal)
  Ethnologue (15th ed.): ywt Yi, Xishan Lalu
- WALS language “Yuchi” (WALS code: yuc)
  other names: Euchee

ISO 639-3 codes to be added (these are languages that are not
in Ethnologue):

- Karankawa = zkk
- WALS language “Coahuilteco” (WALS code: coa) -> ISO 639-3 code: xcw
- WALS language “Timucua” (WALS code: tmc) -> ISO 639-3 code: tjm
- WALS language “Chemakum” (WALS code: cmk) -> ISO 639-3 code: xch
- WALS language “Comecrudo” (WALS code: cmc) -> ISO 639-3 code: xcm

### Language classification/name errors

- Johari: should be Tibeto-Burman (Bodic genus) (not Indo-European, Indic genus) without Ethnologue link.
- Gadaba: should be called “Gutob” (this is not a real error, but the name “Gadaba” for this Munda language is confusing because there is also a Dravidian language by the name “Gadaba”)
- Mikarew: should be in genus 53.5 (Mikarew), not in 53.3 (Lower Ramu)

Genealogical classification changes

3.1 Adamawa-Ubangi [now a subfamily, and renamed (without the -an of Ubangian)]
    3.1.2 Adamawa
        Day
        Doyayo
        Gula Iro
        Koh (Lakka)
        Kosop
        Lua
        Mbum
        Mumuye
        Mundang
        Samba Leko
        Tupuri
        Yag Dii
    3.1.2 Ubangi
        Baka (in Cameroon)
        Barambu
        Dongo
        Gbaya Kara
        Gbeya Bossangoa
        Linda
        Ma
        Mba
        Mdobomo
        Mondunga
        Mündü
        Ndogo
        Ngbaka
        Ngbandi
        Nzakara
        Sango
        Yakoma
        Zande

3.7 Kordofanian [now a subfamily, split into 5 genera]
    3.7.1 Heiban
        Moro
        Otoro
    3.7.2 Katla-Tima
        Katla
    3.7.3 Rashad
        Orig
        Rashad
    3.7.4 Talodi Proper
        Jomang
        Masakin
    3.7.5 Tegem
        Lafofa

6.9 Saharan -> Western Saharan [rename genus]

7.5 Omotic [now a subfamily, split into two genera]
    7.5.1  North Omotic
        Dizi
        Gamo
        Gimira
        Koyra
        Kullo
        Maale
        Ometo
        Shinassha
        Wolaytta
        Yemsa
        Zayse
    7.5.2  South Omotic
        Aari
        Dime
        Hamer
        Kefa
        Moca

30. Andamanese [split into two separate families, corresponding to the two genera in the book]

new 30. Great Andamanese

new 30a. South Andamanese

40. Tor -> Tor-Orya [rename family and split into two genera]
    40.1 Orya
        Orya
    40.2 Tor
        Berik

45.3 Western Sko -> Serra Hills [rename genus]

57.7 Duna-Bogaya -> Duna [rename genus]

57.13 Kutubuan: Fasu should be taken out of Kutubuan and placed in a separate genus called 'Fasu'

57.16 Mairasi-Tanah Merah -> Mairasi [rename genus]

57.19 Timor-Alor-Pantar [split into two genera]
    57.19 Kolana-Tanglapui
        Kolana
        Tanglapui
    57.19a West Timor-Alor-Pantar
        Kui (in Indonesia)
        Woisika

67. Gogodala-Suki [split into two genera]
    67.1 Gogodala
        Gogodala
    67.2 Suki
        Suki

72. Elemen [split into two genera]
    72.1 Eleman Proper
        Orokolo
        Toaripi
    72.2 Tate
        Kaki Ae

78. Baining-Taulil [split into two genera]
    78.1 Baining
        Baining
        Mali
    78.2    Taulil
        Taulil

82. Solomons East Papuan Family [split into three separate families, each language a separate family with one genus with one language]:

new 82. Bilua
    Bilua

new 82a. Lavukaleve
    Lavukaleve

new 82b. Savosavo
    Savosavo

84.7.8 Yangmanic: Wagiman should be split off from Yangmanic as a separate genus called Wagiman

86. Eskimo-Aleut [split into two genera]
    86.1 Aleut
        Aleut
        Aleut (Eastern)
    86.2 Eskimo
    all the other lgs listed in WALS under Eskimo-Aleut

128. Subtiaba-Tlapanec: This should have been listed as a genus within Oto-Manguean (124).

143. Sáliban [split into two genera]
    143.1 Piaroa
        Piaroa
    143.2 Saliba
        Sáliba (in Columbia)

200. Lule-Vilela -> Lule [rename family]
by Matthew S. Dryer
["I am indebted to Harald Hammarström for helpful advice leading
to many of the revisions here from the Genealogical Language
List ..."]


### Feature description error/omission

The text for feature 40 (”Exclusive/Inclusive Distinction in Verbal Inflection”) does not mention that only person affixes in “subject” function have been taken into account.


### Typos

- p. 286: runáját > runájiet
- jacket back: demonstrativennoun and nounndemonstrative
- p. 367; examples 7a and 7b; ergative suffix: – e > -ɹe


### References in electronic version

All errors concern Sharma 1989a/b/c and Sharma 1992

- Tod:
  Lists the data source (for velar nasals) as Sharma 1989a, and lists the reference as Sharma 1989c, whereas in fact these should both be Sharma 1989b.
- Tinani and Gahri:
  The references listed are b and c, when it should only be b. And while the data source is correctly b for Matthew Dryer’s maps, for both it is incorrectly listed as a for the velar nasal map.
- Pattani:
  As with the last two, the references listed are b and c, when it should only be b. But this time it is right for velar nasal, but wrong for my maps, where (at least for some of them) it is listed as a.
- Spitian and Nyamkad:
  Two references are listed, a 1989d and a 1992. But these are the same source, and the correct year is 1992. There should be no 1989d. Furthermore the data source for chapter 9 (The Velar Nasal) is listed as 1989b. Matthew Dryer’s maps are correct as 1992.
- Jad:
  Here the data source (only on Matthew Dryer’s maps) and the reference are both listed as a, which are both wrong, since the source is c.

