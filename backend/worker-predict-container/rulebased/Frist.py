class Frist:
    d = [
        # FRIST FRIST FRIST
        # patterns for "Frist"
        # spätestens jedoch innerhalb von zwei Arbeitstagen (nach deren Zugang)
        {"label": "Frist",
         "pattern": [{"LOWER": {"IN": ["spätestens", "frühestens"]}},
                     {"LOWER": "jedoch"},
                     {"LOWER": "innerhalb"},
                     {"LOWER": "von"},
                     {"LOWER": {"IN": ["zwei", "drei", "vier", "fünf", "sechs",
                                       "sieben", "acht", "neun", "zehn"]}},
                         {"LOWER": "arbeitstagen"}]},
        # {"LEMMA": {"IN": ["Tag", "Arbeitstag", "Woche", "Monat", "Jahr"]}}]},
        # spätestens am zehnten Tage vor der Wahl
        {"label": "Frist",
         "pattern": [{"LOWER": {"IN": ["spätestens", "frühestens"]}},
                     {"LOWER": "am"},
                     {"LOWER": {"IN": ["ersten", "zweiten", "dritten", "vierten",
                                       "fünften", "sechsten", "siebten", "achten",
                                       "neunten", "zehnten"]}},
                     {"LEMMA": {"IN": ["Tag", "Woche", "Monat", "Jahr"]}},
                     {"LOWER": {"IN": ["vor", "nach"]}},
                     {"TAG": "ART"},
                     ]},
        # für jedes Kalenderjahr, jeden Kalendermonat, für jeden angefangenen Kalendermonat
        {"label": "Frist",
         "pattern": [{"LOWER": {"IN": ["für", "in"]}, "OP": "?"},
                     {"LOWER": {"IN": ["jedes", "jedem", "jeden"]}},
                     {"LOWER": {"IN": ["angefangenen", "angefangene", "vergangenen", "vergangene"]}, "OP": "?"},
                     {"LOWER": {"IN": ["kalenderjahr", "kalendermonat", "jahr", "monat", "woche"]}}]},
        # im Kalenderjahr
        {"label": "Frist",
         "pattern": [{"LOWER": {"IN": ["für", "in", "im"]}, "OP": "?"},
                     {"LOWER": {"IN": ["kalenderjahr", "kalendermonat", "jahr", "monat", "woche"]}}]},
        # bis zum Ablauf der in § 5 Abs. 5 festgelegten Fristen
        {"label": "Frist",
         "pattern": [{"LOWER": "bis"},
                     {"LOWER": "zum"},
                     {"LEMMA": "Ablauf"},
                     {"TAG": "ART"},
                     {"LOWER": "in"},
                     {"TEXT": "§"},
                     {"TAG": "CARD"},
                     {"TEXT": {"IN": ["Abs.", "Absatz"]}},
                     {"TAG": "CARD"},
                     {"LOWER": "festgelegten"},
                     {"LEMMA": "Frist"}]},
        # Frist nach §3 Absatz 3 Satz 2 Nummer 1
        {"label": "Frist",
         "pattern": [{"LEMMA": "Frist"},
                     {"LOWER": "nach"},
                     {"TEXT": "§"},
                     {"TAG": "CARD"},
                     {"TEXT": {"IN": ["Abs.", "Absatz"]}, "OP": "?"},
                     {"TAG": "CARD", "OP": "?"},
                     {"LEMMA": "Satz", "OP": "?"},
                     {"TAG": "CARD", "OP": "?"},
                     {"LEMMA": "Nummer", "OP": "?"},
                     {"TAG": "CARD", "OP": "?"}
                     ]},
        # bis der rückständige Beitrag oder Beitragsvorschuß entrichtet worden ist
        {"label": "Frist",
         "pattern": [{"LOWER": "bis"},
                     {"TAG": "ART"},
                     {"TAG": "ADJA", "OP": "?"},
                     {"LEMMA": {"IN": ["Beitrag", "Gebühr", "Entgeld"]}},
                     {"LOWER": "oder", "OP": "?"},
                     {"LEMMA": {"IN": ["Beitragsvorschuß", "Vorschuß"]}, "OP": "?"},
                     {"LOWER": {"IN": ["entrichtet", "bezahlt"]}},
                     {"LOWER": "worden"},
                     {"LOWER": "ist"}]},
        # bis zur Vollendung des 21. Lebensjahres
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["bis"]}},
                     {"LOWER": "zur"},
                     {"LEMMA": "Vollendung"},
                     {"TAG": "ART"},
                     {"TAG": "ADJA"},
                     {"LEMMA": "Lebensjahr"}]},
        # Double Prep: (von) bis zu vier Jahren
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["von", "für"]}, "OP": "?"},
                     {"LOWER": "bis"},
                     {"LOWER": "zu"},
                     {"TAG": "CARD"},
                     {"LEMMA": {"IN": ["Jahr", "Monat", "Woche", "Tag", "Stunde"]}}]},
        # (von) bis zu einem Jahr ("einem" = ART)
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["von", "für"]}, "OP": "?"},
                     {"LOWER": "bis"},
                     {"LOWER": "zu"},
                     {"TAG": "ART"},
                     {"LEMMA": {"IN": ["Jahr", "Monat", "Woche", "Tag", "Stunde"]}}]},
        
        # in den letzten drei Jahren
        {"label": "Frist",
         "pattern": [{"LOWER": "in"},
                     {"TAG": "ART", "MORPH": "Definite=Def"},
                     {"LOWER": "letzten"},
                     {"TAG": "CARD"},
                     {"LEMMA": {"IN": ["Jahr", "Monat", "Woche", "Tag", "Stunde"]}}]},
        # bis zum Ende ihrer Befristung; von dem Beginn der Frist an(?)
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["bis", "von"]}},
                     {"TAG": "APPRART"},
                     {"LEMMA": {"IN": ["Ende", "Beginn", "Anfang"]}},
                     {"TAG": "PPOSAT"},
                     {"TAG": "NN"},
                     {"TAG": "APPO", "OP": "?"}]},
            # beim Eintritt in den Ruhestand; (Beim Austritt aus dem Verein)
        {"label": "Frist",
         "pattern": [{"TAG": "APPRART"},
                     {"TAG": "NN"},
                     {"LEMMA": {"IN": ["Eintritt", "Austritt"]}},
                     {"TAG": "APPR"},
                     {"TAG": "NN"}]},
        # bis zum Schuleintritt; bis zu dem Schuleintritt
        {"label": "Frist",
         "pattern": [{"LOWER": {"IN": ["bis", "ab", "vor"]}},
                     {"LOWER": {"IN": ["zum", "zur", "zu"]}},
                     {"TAG": "ART", "OP": "?"},
                     {"LOWER": {"IN": ["schuleintritt", "beginn", "anfangsdatum"]}}
                     ]},
        # bei der Eheschließung
        {"label": "Frist",
         "pattern": [{"LOWER": {"IN": ["bei", "vor", "mit", "zu"]}},
                     {"TAG": "ART"},
                     {"LOWER": {"IN": ["schuleintritt", "eheschließung", "erreichen"]}}
                     ]},
        # bis zum 24. Dezember 2024
        {"label": "Frist",
         "pattern": [{"TAG": "APPR"},
                     {"TAG": "ART", "MORPH": "Definite=Def"},
                     {"TAG": "ADJA"},
                     {"LEMMA": {"IN": ["Januar", "Februar", "März", "April",
                                       "Mai", "Juni", "Juli", "August",
                                       "September", "Oktober", "November", "Dezember"]}},
                     {"LIKE_NUM": True}]},
        # see frist_prep_x.md Three elements, Summary
        # für das betreffende Haushaltsjahr
        {"label": "Frist",
         "pattern": [{"TAG": "APPR", "LEMMA": "für"},
                     {"TAG": "ART"},
                     {"TAG": "ADJA"},
                     {"TAG": "NN", "LEMMA": {"IN": ["Haushaltsjahr", "Jahr", "Monat", "Woche", "Tag"]}}
                     ]},
        # vor (dem) Beginn der Maßnahme
        {"label": "Frist",
         "pattern": [{"LEMMA": "vor"},
                     {"TAG": "ART", "OP": "?"},
                     {"TAG": "NN", "LEMMA": {"IN": ["Beginn", "Ausstellung", "Ablauf"]}},
                     {"TAG": "ART"},
                     {"TAG": "NN"}]},
        # zur Zeit der Erklärung
        {"label": "Frist",
         "pattern": [{"TAG": "APPRART"},
                     {"LEMMA": "Zeit"},
                     {"TAG": "ART"},
                     {"TAG": "NN", "LEMMA": "Erklärung"}]},
        # auf Dauer angelegte Lebensform
        {"label": "Frist",
         "pattern": "auf Dauer angelegte Lebensform"},
        # zeitlich befristete Erziehungshilfe
        {"label": "Frist",
         "pattern": [{"LOWER": "zeitlich"},
                     {"LOWER": "befristete"},
                     {"LEMMA": {"IN": ["Hilfe", "Erziehungshilfe"]}}]},
        # bis zur Entscheidung
        {"label": "Frist",
         "pattern": [{"LEMMA": "bis"},
                     {"TAG": "APPRART"},
                     {"LEMMA": {"IN": ["Entscheidung", "Wahl", "Erteilung"]}}]},
        # (spätestens) drei Jahre nach/vor (556.conll)
        {"label": "Frist",
         "pattern": [{"LOWER": {"IN": ["spätestens", "frühestens",
                                       "mindestens", "höchstens"]}},
                     {"TAG": "CARD"},
                     {"LEMMA": {"IN": ["Jahr", "Monat", "Woche", "Tag"]}},
                     {"LEMMA": {"IN": ["nach", "vor"]}}
                     ]},
        # vor dem Eröffnungsantrag; vor der Inanspruchnahme
        {"label": "Frist",
         "pattern": [{"LEMMA": "vor"},
                     {"TAG": "ART"},
                     {"LEMMA": {"IN": ["Eröffnungsantrag", "Inkrafttreten",
                                       "Entscheidung", "Zeitpunkt", "Inanspruchnahme"]}}]},
        # innerhalb einer bestimmten Frist
        {"label": "Frist",
         "pattern": [{"LOWER": "innerhalb"},
                     {"TAG": "ART"},
                     {"LEMMA": "bestimmt"},
                     {"LEMMA": {"IN": ["Frist", "Zeit", "Zeitraum"]}}]},
        # binnen (innerhalb) einer Woche
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["binnen", "innerhalb", "für"]}},
                     {"TAG": "ART"},
                     {"TAG": "NN", "LEMMA": {"IN": ["Woche", "Monat", "Jahr", "Beurteilungszeitraum"]}}]},
        # binnen (innerhalb) zweier Wochen
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["binnen", "innerhalb"]}},
                     {"TAG": "ADJA"},
                     {"TAG": "NN", "LEMMA": {"IN": ["Woche", "Monat", "Jahr"]}}]},
        # binnen zwei Wochen
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["binnen", "innerhalb", "für"]}},
                     {"TAG": "CARD"},
                     {"TAG": "NN", "LEMMA": {"IN": ["Woche", "Monat", "Jahr"]}}]},
        # für ein Jahr, mit dem Tag, (spätestens) mit der Frist
        {"label": "Frist",
         "pattern": [
                     {"LEMMA": {"IN": ["für", "ab", "mit"]}},
                     {"TAG": "ART"},
                     {"LEMMA": {"IN": ["Jahr", "Zeitraum", "Tag", "Woche", "Monat",
                                       "Frist"]}}]},
        # spätestens mit
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["spätestens", "frühestens",
                                       "mindestens", "höchstens"]}},
                      {"LOWER": "mit"}]
         },
        # ab einem Jahr
        # für (mindestens) zwei Jahre, von (höchstens) vier Wochen
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["für", "von"]}},
                     {"LOWER": {"IN": ["mindestens", "wenigstens", "längstens", "höchstens"]},
                      "OP": "?"},
                     {"TAG": "CARD"},
                     {"LEMMA": {"IN": ["Jahr", "Monat", "Woche", "Tag", "Stunde"]}}]},
        # nach der Beendigung; unverzüglich nach Halterwechsel; nach deren Ablauf (?)
        {"label": "Frist",
         "pattern": [{"LEMMA": "unverzüglich", "OP": "?"},
                     {"LEMMA": "nach"},
                     {"TAG": "ART", "OP": "?"},
                     {"TAG": "NN", "LEMMA": {"IN": ["Halterwechsel", "Antragstellung", "Beendigung", "Ablauf"]}}]},
        # erst nach Empfang; nach deren Ablauf
        {"label": "Frist",
         "pattern": [{"LOWER": "erst", "OP": "?"},
                     {"LOWER": {"IN": ["nach", "vor", "seit", "mit"]}},
                     {"TAG": "PDS", "OP": "?"},
                     {"LEMMA": {"IN": ["Empfang", "Ablauf", "Beginn", "Beendigung"]}}]},
        # vor Beginn; nach Anhörung; nach Einsichtnahme
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["vor", "bei", "nach"]}},
                     {"LEMMA": {"IN": ["Beginn", "Ausstellung", "Antragstellung",
                                       "Anhörung", "Ablauf", "Abschluss",
                                       "Einsichtnahme"]}}]},
        # zum Zeitpunkt, zur Zeit
        {"label": "Frist",
         "pattern": [{"TAG": "APPRART"},
                     {"LEMMA": {"IN": ["Zeitpunkt", "Zeit"]}}]},
        # je Jahr
        {"label": "Frist",
         "pattern": [{"LOWER": "je"},
                     {"LEMMA": {"IN": ["Jahr", "Monat", "Woche", "Tag", "Stunde"]}}]},
        # angemessenen Frist
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["angemessen", "ausreichend", "hinreichend"]}},
                      {"LEMMA": {"IN": ["Frist", "Zeit", "Zeitraum"]}}]},
        # vom 1. Januar 2008 an
        {"label": "Frist",
         "pattern": [{"LOWER": "vom", "OP": "?"},
                     {"TEXT": {"IN": ["1.", "15.", "30.", "31."]}},
                     {"TEXT": {"IN": ["Januar", "Februar", "März", "April", "Mai", "Juni",
                                      "Juli", "August", "September", "Oktober",
                                      "November", "Dezember"]}},
                     {"IS_DIGIT": True},
                     {"LOWER": "an", "OP": "?"}
                     ]},
        # vier Wochen; (alle) zwei Jahre
        {"label": "Frist",
         "pattern": [{"LOWER": "alle", "OP": "?"},
                     {"TAG": "CARD"},
                     {"LEMMA": {"IN": ["Tag", "Woche", "Monat", "Jahr"]}}]},
        # 30. Juni 
        {"label": "Frist",
         "pattern": [{"TEXT": {"IN": ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.",
                                      "11.", "12.", "13.", "14.", "15.", "16.", "17.", "18.", "19.", "20.",
                                      "21.", "22.", "23.", "24.", "25.", "26.", "27.", "28.", "29.", "30.", "31."]}},
                     {"TEXT": {"IN": ["Januar", "Februar", "März", "April", "Mai", "Juni",
                                      "Juli", "August", "September", "Oktober",
                                      "November", "Dezember"]}}]},
        # (vom) 29. Juni 2017
        {"label": "Frist",
         "pattern": [{"LOWER": {"IN": ["vom", "zum"]}, "OP": "?"},
                     {"TEXT": {"IN": ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.",
                                      "11.", "12.", "13.", "14.", "15.", "16.", "17.", "18.", "19.", "20.",
                                      "21.", "22.", "23.", "24.", "25.", "26.", "27.", "28.", "29.", "30.", "31."]}},
                     {"TEXT": {"IN": ["Januar", "Februar", "März", "April", "Mai", "Juni",
                                      "Juli", "August", "September", "Oktober",
                                      "November", "Dezember"]}},
                     {"TAG": "CARD"}]},
        # special patterns
        # nach der vorherigen Befassung
        {"label": "Frist",
         "pattern": "nach der vorherigen Befassung"},
        # in den sechs der Wahl oder Abstimmung vorangehenden Monates
        {"label": "Frist",
         "pattern": [{"LOWER": "in"},
                     {"TAG": "ART"},
                     {"TAG": "CARD"},
                     {"TAG": "ART"},
                     {"LEMMA": "Wahl"},
                     {"LOWER": {"IN": ["oder", "und"]}},
                     {"LEMMA": "Abstimmung"},
                     {"LEMMA": "vorangehend"},
                     {"LEMMA": "Monat"}]},
        # one word expressions
        # Caution: lemma is sensitive to capitalization, that is why we need both
        # "unverzüglich" and "Unverzügich"
        {"label": "Frist",
         "pattern": [{"LEMMA": {"IN": ["unverzüglich", "Unverzüglich", "jederzeit", "sofortig",
                                       "vorzeitig", "frühzeitig", "nachdem", "jährlich",
                                       "umgehend", "gleichzeitig", "zeitnah", "vorläufig",
                                       "bisher", "früheren", "Bezugszeitraum",
                                       "dauerhaft", "während", "nachträglich", "regelmäßig",
                                       "monatlich", "sobald", "Pflichtbeitragszeit",
                                       "Anrechnungszeit",  "Berücksichtigungszeit"]}}]}]


