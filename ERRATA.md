# Errata

As of September 28, 2026, https://github.com/cldf-datasets/wals/issues lists 21 open issues related to the WALS dataset.
Below we list the issues confirmed by one of the WALS editors or authors of the relevant features.


## Fula corrections

Via Matthew Dryer

> One of the sources for many datapoints for Fulfulde (Adamawa) is Arnott (1970).  However, Arnott (1970) actually deals with Fulfulde (Nigerian) not Fulfulde (Adamawa).  What needs to be done, at least in the long run, is to move these from Fulfulde (Adamawa) to Fulfulde (Nigerian).  This is not straightforward, however, since many of the datapoints for Fulfulde (Adamawa) are based both on Arnott and on one or more sources that are correctly sources for Fulfulde (Adamawa).  What I suggest is that you leave all the datapoints in my chapters that use Arnott as a source where they are now, and wait until I next update my WALS chapters, which will “automatically” take care of this.  However, for other people’s chapters, you will have to do something (though you might wait until I update my data).  For other people’s chapters, these datapoints need to be moved to Fulfulde (Nigerian):

ID   | Value                                       | Feature                                                  | Sources
---  | ---                                         | ---                                                      | ---
36A  | Associative same as additive plural         |  The Associative Plural                                  | Arnott 1970: 400; Labatut 1973: 62
49A  | No morphological case-marking               |  Number of Cases                                         | Arnott 1970: 139-148, App. 3
50A  | No case-marking                             | Asymmetrical Case-Marking                                | Arnott 1970: 139-148, App. 3
58A  | Absent                                      | Obligatory Possessive Inflection                         | Arnott 1970
58B  | None reported                               |  Number of Possessive Nouns                              | Arnott 1970
59A  | Two classes                                 | Possessive Classification                                | Arnott 1970
72A  | Maximal system                              | Imperative-Hortative Systems                             | Arnott 1970: 248-252, 300-302
74A  | Affixes on verbs                            | Situational Possibility                                  | Arnott 1970: 300
75A  | Affixes on verbs                            | Epistemic Possibility                                    | Arnott 1970: 274f.
76A  | Overlap for either possibility or necessity | Overlap between Situational and Epistemic  Modal Marking | Arnott 1970: 302-304
100A | Accusative                                  | Alignment of Verbal Person Marking                       | Arnott 1970: 183, 212
102A | Both the A and P arguments                  | Verbal Person Marking                                    | Arnott 1970: 212
103A | No zero realization                         | Third Person Zero of Verbal Person Marking               | Arnott 1970: 212
104A | P precedes A                                | Order of Person Markers on the Verb                      | Arnott 1970: 212
107A | Present                                     | Passive Constructions                                    | Arnott 1970: 179
125A | Deranked                                    | Purpose Clauses                                          | Arnott 1970: 380
126A | Balanced/deranked                           | 'When' Clauses                                           | Arnott 1970: 38, 320-1, 326
127A | Balanced                                    | Reason Clauses                                           | Arnott 1970: 38
136A | M-T pronouns, paradigmatic                  | M-T Pronouns                                             | Arnott 1970
136B | m in first person singular                  | M in First Person Singular                               | Arnott 1970
137A | No N-M pronouns                             | N-M Pronouns                                             | Arnott 1970
137B | m in second person singular                 | M in Second Person Singular                              | Arnott 1970

> There is one complication and that is that chapter 36 uses Arnott 1970: 400; Labatut 1973: 62 and Arnott is a source for Fulfulde (Nigerian) while Labatut is a source for Fulfulde (Adamawa). I suggest that this datapoint be moved to Fulfulde (Nigerian) and that Labatut simply be removed as a source.

> Fifth, the WALS entry for Fulfulde (Nigerian) (=Fula (Nigerian)) at http://wals.info/languoid/lect/wals_code_fni lists feature values for features 95A, 96A, and 97A, which is necessarily erroneous, since these three features are based on other features and this language is not coded for those other features. (However, once the data for Arnott is moved to Fulfulde (Nigerian), there WILL be data for these.)  But this raises the question whether there might be other errors of this sort. If it's not too difficult, would it be possible for you to write a script to see whether there are any other languages with values for one or more of these three features, but no value for one or both of the features that feature is based on:

- 95A is based on 83A and 85A
- 96A is based on 83A and 90A
- 97A is based on 83A and 87A 


## Update datapoint Haida / Alignment of Case Marking of Pronouns

Via Matthew Dryer:

> One of the datapoints for feature 99A needs to be changed, namely the [datapoint for Haida](https://wals.info/valuesets/99A-hai), must be changed from Neutral to Active-Inactive. This also decreases the number of Neutral languages from 79 to 78 and increases the number of Active-Inactive languages from 3 to 4.

In addition, two example sentences need to be replaced, as follows:

-  [igt-1212](https://wals.info/example/igt-1212)
   ```
   daa-hl@	       gyaaxa
   you.SG.AGT-IMP  stand
   ‘you stand up!’
  ```

- [igt-1213](https://wals.info/example/igt-1213)
  ```
  dang-gw@	    q’ud-uus?
  you.SG.PAT-Q  be.hungry-BIASED
  ‘you’re hungry, aren’t you?’
  ```

Source: Enrico 2003, p. 121, 137


## Correct coding of Orok for feature 87A

Via Bernard Comrie

> For a current research project I needed to ascertain against WALS which basically head-final (OV & Po & GN) languages in Asia have the attributive adjective after the head noun. I was surprised to see the Tungusic language Orok among these languages. I can assure you without hesitation that this assignment for Orok is incorrect, Orok has basic AN order. But the problem lies in a gross translation error from Polish into English in what I take to be your source.

> Please note that I am actually referring to the edition of Piłsudski  published by De Gruyter, which I have been able to access piecemeal via Google Books in this period of closed libraries, so I can't be 100% sure what the version you accessed says. I have attached images of the relevant pages/parts of pages.

> The crucial sentence relating to adjective order is as follows in Polish, with glossing and translation:

```
Przymiotniki   stoją          zawsze (?) przed  rodzajnikami
Przymiotnik-i  stoj-ą         zawsze (?) przed  rodzajnik-ami
adjective-PL   stand-PRS.3PL  always (?) before noun-PL.INS
'Adjectives always (?) stand before nouns.'
```

> This comes out in the English translation in the source incorrectly as "Adjectives always (?) follow the words (nouns) they determine".

> The Orok example given in the original, with glossing and translation, is as follows:

```
byrymi ula
byrymi ula
clever reindeer
‘clever reindeer’
```

> The example clearly exemplifies AN order.

> There is one terminological oddity in the Polish sentence. While "przymiotnik" is the usual Polish term for 'adjective', "rodzajnik" is not the usual term for 'noun'. The volume in question  does sometimes have the standard term "rzeczownik" for 'noun', but frequently has "rodzajnik" in what is clearly this sense. The translator(s) usually use(s) "noun" in English, though in the above example they hedge with both "word" and "noun". In Polish linguistic terminology "rodzajnik" means 'article' (as in "(in)definite ~"), a PoS absent from Polish and Orok. The Polish word is derived from "rodzaj" 'gender' (also 'kind, sort' in non-technical usage). It is presumably a calque on the home-grown German term for an article, "Geschlechtswort", literally 'gender-word', on the basis that the article in many languages, including German, indicates the gender of a noun. I can only speculate as to why Piłsudski used this term in the sense 'noun' -- 'verb' is "czasownik" in Polish because time/tense ("czas") is one of the main categories that characterize it, so maybe 'noun' is named after 'gender' -- and I've no idea whether this usage is idiosyncratic to him or was current in his circle. Note also that the part of the English "translation" that says "[the words] they determine" is an interpretation, not a translation of the original.


## Correct coding Feature 39 (inclusive/exclusive), Language code map (Mapudungun)

Via Michael Cysouw

> The classification of Mapudungun (map) does not fit with the sources as given for Feature 39 (Inclusive/Exclusive Distinction in Independent Pronouns). 

> Please change from type 2 ('We' the same as 'I') to type 3 (No inclusive/exclusive).

