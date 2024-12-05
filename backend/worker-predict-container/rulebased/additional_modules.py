########################################
# Creating patterns for the EntityRuler
########################################


def match_bedingung(doc, epatterns):
    for i, token in enumerate(doc):
        if (token.lemma_ in ['wenn', 'Wenn', 'soweit', 'Soweit', 'sofern', 'Sofern', 'falls', 'Falls']):
            if doc[i-1].text in ['.', ',', '(', ')']:
                subclause = [token.text]
                j = i+1
                while j < len(doc) and doc[j].text not in ['.', ',']:
                    subclause.append(doc[j].text)
                    j = j + 1
                temp = []
                for tok in subclause:
                    temp.append({"TEXT": tok})
                epatterns.append({"label": "Bedingung", "pattern": temp})
        # Fine-grained POS is in token.tag_, not token.pos_                
        elif (token.tag_ in ['VVFIN', 'VAFIN', 'VMFIN']):
            # NOT the same as token.lemma_, esp. NOT comma!
            if doc[i-1].text in ['.', ';', '(', ')']:
                subclause = [token.text]
                j = i+1
                while j < len(doc) and doc[j].text not in ['.', ',']:
                    subclause.append(doc[j].text)
                    j = j + 1
                    temp = []
                    for tok in subclause:
                        temp.append({"TEXT": tok})
                        epatterns.append({"label": "Bedingung", "pattern": temp})
        # relative clauses as "Bedingung"
        elif token.tag_ == 'PRELS':
            if doc[i-2].tag_ == 'NN':
                subclause = [token.text]
                j = i+1
                while j < len(doc) and doc[j].text not in ['.', ',']:
                    subclause.append(doc[j].text)
                    j = j + 1
                    temp = []
                    for tok in subclause:
                        temp.append({"TEXT": tok})
                        epatterns.append({"label": "Bedingung", "pattern": temp})
                        
    return epatterns


def match_aktion(doc, epatterns):
    # From analysis of manual annotations
    # nomlist = ["Bestimmung", "Ausstellung", "Anmeldung",
    #            "Entscheidung", "Beendigung", "Auslegung",
    #            "Vollendung", "Antragstellung", "Ersetzung",
    #            "Befristung", "Erteilung", "Prüfung", "Verwertung",
    #            "Weiterleitung"]
    nomlist = ["Beratung", "Vereidigung", "Befragung", "Einzelbetreuung", "", "Messung", "Beglaubigung", "Registrierung", "Genehmigungen", "Aufhebung", "Vertretung", "Einreichung", "Hilfeleistung", "Apothekenbetriebsordnung", "Behandlung", "Benutzung", "Sammlung", "Aufforderung", "Neuanmeldung", "Zustellung", "Meldung", "Errichtung", "Berufsbildung", "Amtshandlungen", "Arbeitsvermittlung", "Fortbildung", "Stellung", "Verkehrszulassung", "Einberufung", "Ablehnung", "Bestimmung", "Pauschalierung", "Beteiligung", "Ablegung", "Besichtigungen", "Heimerziehung", "Vermeidung", "Mitteilung", "Ausstellung", "Erreichung", "Anmeldung", "Entscheidungen", "Allgemeinzuteilung", "Ausbildungsvermittlung", "Bewertung", "Frequenzzuteilung", "Anfertigung", "Zustimmung", "Entscheidung", "Einhaltung", "Umwandlung", "Nachholung", "Einzelfallentscheidung", "Rentenberatung", "Befreiung", "Versendung", "Bestellung", "Speicherung", "Einzelvertretung", "Auslegung", "Bildung", "Zuwendungen", "Betreuung", "Begleitung", "Verleihung", "Verbindung", "Verarbeitung", "Ausschreibung", "Verordnung", "Anwendung", "Glaubhaftmachung", "Erstattung", "Abstimmungen", "Nachtragung", "Einwilligung", "Aktualisierung", "Berichtigung", "Wahrnehmung", "Anstellung", "Ausgleichsleistungen", "Vereinbarung", "Weiterleitung", "Darstellung", "Datenbeobachtung", "Sicherheitsleistung", "Ausgleichszahlung", "Versicherung", "Nummerierung", "Antragstellung", "Erstaufforstung", "Anerkennung", "Vorbereitung", "Verhandlung", "Feststellung", "Wiederholungsbefragungen", "Beurkundung", "Verteilung", "Durchsetzung", "Bekanntmachung", "Identifizierung", "Beseitigung", "Zulassung", "Eintragung", "Umschreibung", "Rechtshandlungen", "Teilung", "Versorgung", "Freiheitsentziehung", "Verbesserung", "Berufsausbildung", "Umsetzung", "Stundung", "Nachzahlung", "Leistungen", "Bereithaltung", "Zuteilung", "Herstellung", "Erteilung", "Umschulung", "Stilllegung", "Feststellungen", "Genehmigung", "Sicherstellung", "Verwendung", "Anleitung", "Aufstellung", "Pflegeberatung", "Beurteilung", "Geltendmachung", "Rechnungslegung", "Beibringung", "Absendung"]
    for i, token in enumerate(doc):
#        if token.lemma in nomlist and ((token.lemma_[-3:] == 'ung') or (token.lemma_[-5:] == 'ungen')):
        if token.text in nomlist:
#        if (token.lemma_[-3:] == 'ung') or (token.lemma_[-5:] == 'ungen'):
            epatterns.append({"label": "Aktion",
                              "pattern": [{"TEXT": token.text}]})
        # elif token.tag_ == "VVIZU":
        #     epatterns.append({"label": "Aktion",
        #                       "pattern": [{"TEXT": token.text}]})
    # epatterns.append({"label": "Aktion",
    #                   "pattern": [{"TAG": "VVIZU"}]})
    # epatterns.append({"label": "Aktion",
    #                   "pattern": [{"TAG": "VVINF"}]})
    return epatterns


def match_signalwort(doc, epatterns):
    # Originally, this pattern looked only for modal verbs VMFIN.
    # This version adds patterns for all the examples listed in
    # the document "Annotationsrichtlinien" from 10 January 2024.
    epatterns.append({"label": "Signalwort",
                      "pattern": [{"LOWER": "auf"}, {"LEMMA": "Antrag"}]})
    epatterns.append({"label": "Signalwort",
                      "pattern": [{"LOWER": "auf"}, {"LEMMA": "Verlangen"}]})
    epatterns.append({"label": "Signalwort",
                      "pattern": [{"LOWER": "bei"}, {"LEMMA": "Bedarf"}]})
    epatterns.append({"label": "Signalwort",
                      "pattern": [{"LEMMA": "verpflicht"}]})
    for token in doc:
        if token.tag_ == "VMFIN":
            epatterns.append({"label": "Signalwort",
                              "pattern": [{"TEXT": token.text}]})
        elif token.lemma_ == "erforderlich":
            epatterns.append({"label": "Signalwort",
                              "pattern": [{"LEMMA": token.lemma_}]})
        elif token.lemma_ == "zweckgebunden":
            epatterns.append({"label": "Signalwort",
                              "pattern": [{"LEMMA": token.lemma_}]})
    return epatterns

def match_mitwirkender(doc, epatterns):
    mw = ["Bundesministerium für Verkehr und digitale Infrastruktur",
          "Max Rubner-Institut",
          "bischöflichen Behörde",
          "Bundesministerium des Innern und für Heimat",
          "Bundesministeriums für Arbeit und Soziales",
          "erkennende Gericht",
          "Körperschaften des öffentlichen Rechts",
          "Bundesministeriums für Ernährung und Landwirtschaft",
          "Deutschen Patent - und Markenamts",
          "Bundesamt für Wirtschaft und Ausfuhrkontrolle",
          "Bundesamt für Migration und Flüchtlinge",
          "Bundesministerium für Wirtschaft und Energie",
          "Sektion Verkehrspsychologie im Berufsverband Deutscher Psychologinnen und Psychologen",
          "obersten Landesjugendbehörden",
          "gesetzlicher oder bevollmächtigter Vertreter",
          "gesetzlichen Vertreters",
          "Bundesamt für Verfassungsschutz",
          "Bundesinstitut für Arzneimittel und Medizinprodukte",
          "Bundesministerium der Justiz und für Verbraucherschutz",
          "vorsitzenden Person",
          "Militärischen Abschirmdienst",
          "bekannte informationspflichtige Stellen",
          "statistischen Ämter der Länder",
          "für die metrologische Überwachung zuständigen Behörden",
          "Lebensmittel - oder Futtermittelunternehmers",
          "Statistische Bundesamt Statistische Bundesamt",
          "Träger der Krankenversicherung",
          "Bundesministerium des Innern, für Bau und Heimat",
          "Bundesamt für Verbraucherschutz und Lebensmittelsicherheit",
          "Gemeinsame Bundesausschuss",
          "Einrichtungen der freiwilligen Selbstkontrolle",
          "anderer Personen",
          "Bundesministerium der Finanzen",
          "Bundesministerium für Ernährung und Landwirtschaft",
          "Bundesarbeitsgemeinschaft der Integrationsämter",
          "Gerichtshofes der Europäischen Union",
          "amtliche Vertretung der Bundesrepublik Deutschland",
          "öffentlich-rechtlichen Entsorgungsträger",
          "zentrale Aufsichtsstelle der Länder für den Jugendmedienschutz",
          "Bundesagentur für Arbeit",
          "Bundesministerium für Familie, Senioren, Frauen und Jugend"]
    mwsg = ["Dritte", "Bundesnachrichtendienst", "Arzt", "Verfassungsschutzbehörde", "Verwaltungsbehörden",
            "Stellen", "Personen", "Hochschule", "Zulassungsausschusses", "Prüfstelle", "Bewertungsstellen",
            "Vertreters", "Tierschutzbeauftragte", "Bundes", "Sozialarbeiter", "Landesjugendämter",
            "Zahnärzten", "Gebrauchsmusterstelle", "Planfeststellungsbehörde", "Dienstbehörde",
            "Monopolkommission", "Ärzte", "Ordensoberen", "Einrichtungen", "Standesbeamten",
            "Einrichtung", "Internet-Beschwerdestellen", "Religionsgemeinschaft", "Arbeitgeber",
            "Bundespolizei", "Überwachungsstelle", "Bundesbeauftragten", "Eigentümers",
            "Kindertagespflegeperson", "Krankenversicherung", "Bundesnetzagentur", "Zulassungsausschuss",
            "Träger", "Direktoren", "Familiengerichts", "Oberlandesgericht", "Beistand",
            "Kommission", "Ärzten", "Flüchtlinge", "Gebrauchsmusterabteilungen", "Deutscher",
            "Rehabilitationsträger", "Berater", "Staatenlose", "Personal", "Gericht",
            "Personensorgeberechtigten", "Bundesbank", "Landesplanungsbehörde", "Rechtsanwalt",
            "Tageseinrichtungen", "Fahrzeugführers", "Staatsanwaltschaften", "Mitgliedstaat",
            "Notars", "Vertreterin", "Landesregierung", "Zollkriminalamt", "Landesbehörden",
            "Pflegefachkräfte", "Geschäftsleiters", "Familienangehörigen", "Vertragsarzt",
            "Behörden", "Trägers", "Bundesministerium", "Beschäftigten", "Bundesausschuss",
            "Rücknahmestelle", "Landeskirchenamtes", "Gerichts", "Pflegeberaterinnen", "Annahmestelle",
            "Bundesbeauftragte", "Grenzzollstelle", "Prüfungsstelle", "Ausländer", "Personalrats",
            "Umweltbehörde", "Polizeibehörden", "Landesbehörde", "Eigentümer", "Wohnform",
            "Jugendämter", "Hauptfürsorgestellen", "Sachverständige", "Vertragsärztin", "Erziehungsberechtigten",
            "Kreiswahlleiter", "Pflegeberater", "Sozialversicherungsfachangestellte", "Einsatzstelle",
            "Landesverbände", "Rechtsnachfolger", "Zentralstelle", "Schule", "Berufsgenossenschaft",
            "Kindes", "Technische", "Arbeitgebers", "Tageseinrichtung", "Bundesbehörde",
            "Betrieb", "Oberbehörde", "Bundesrechnungshof", "Verband", "Bundeskriminalamt", "Dienst",
            "Eltern", "Pflegeberatern", "Betriebsrat", "Person", "Auftraggeber", "Kreiswehrersatzamt",
            "Landesregierungen", "Bundesregierung", "Organisation", "Wahlvorsteher", "Hauptverwaltung",
            "Rehabilitationsträgern", "Bundestages", "Pflegekassen", "Personalrat", "Bevollmächtigten",
            "Stelle", "Vertretung", "Bundesrates", "Behörde", "Institut", "Länder", "Betriebsrats",
            "Ansprechstellen", "Sozialleistungsträger", "Kreise", "Prüfungsverband", "Kindertagespflege",
            "Koordinierungsstellen", "Schuldner", "Sparkassen", "Leistungserbringers", "Gemeinde"]
    for pers in mw:
        epatterns.append({"label": "Mitwirkender",
                          "pattern": pers})
    for pers in mwsg:
        epatterns.append({"label": "Mitwirkender",
                          "pattern": pers})
    return epatterns

def match_handlungsgrundlage(doc, epatterns):
    hlgwords = ["§", "Rechtsnorm", "Rechtsnormen", "Verordnung", "Verordnungen",
                "Rechtsverordnung", "Rechtsverordnungen",  
                "Absatz", "Absatzes", "Abs.", "Absätze", "Satz", "Sätze", 
                "Sätzen", "Satzes", "Nr.", "Buchstabe", "Buchstaben",
                "Artikel", "Artikeln", "Artikels", "EG", "ABl"
                "Anforderung", "Anforderungen", "Verwaltungsvorschrift", "Verwaltungsvorschriften" 
                "Wertpapierhandelsgesetzes", 
"Stromsteuergesetzes", 
"Altersteilzeitgesetzes", 
"Beurkundungsgesetzes", 
"Versicherungsaufsichtsgesetzes", 
"Entwicklungshelfer-Gesetzes", 
"Bundeskindergeldgesetzes", 
"Partnerschaftsgesellschaftsgesetzes", 
"Einsatz-Weiterverwendungsgesetzes", 
"Grundgesetzes", 
"Betriebsverfassungsgesetzes", 
"Gerichtsverfassungsgesetzes", 
"Jugendfreiwilligendienstegesetzes", 
"Verwaltungsvollstreckungsgesetzes", 
"Bundesberggesetzes", 
"Justizentschädigungsgesetzes", 
"Statistikregistergesetzes", 
"Genossenschaftsgesetzes", 
"Beamtenversorgungsgesetzes", 
"Abfallgesetzes", 
"Personenstandsgesetzes", 
"Kraft-Wärme-Kopplungsgesetzes", 
"Bundesverfassungsschutzgesetzes", 
"Patentgesetzes", 
"Bundesausbildungsförderungsgesetzes", 
"Bundesversorgungsgesetzes", 
"Aufenthaltsgesetzes", 
"Asylgesetzes", 
"Bundes-Immissionsschutzgesetzes", 
"Einführungsgesetzes", 
"Asylbewerberleistungsgesetzes", 
"Patentkostengesetzes", 
"Energiesteuergesetzes", 
"Kreditwesengesetzes", 
"Justizvergütungsgesetzes", 
"Steinkohlefinanzierungsgesetzes", 
"Gebrauchsmustergesetzes", 
"Eichgesetzes", 
"Verwaltungsverfahrensgesetzes", 
"Bundesvertriebenengesetzes", 
"Transsexuellengesetzes", 
"Soldatengesetzes", 
"Bundesverfassungsgerichtsgesetzes", 
"Hochschulrahmengesetzes", 
"Pflanzenschutzgesetzes"

                ]
    vbgwords = ["und", "sowie", "die", ",", "des", "(", ")", "/"]
    for i, token in enumerate(doc):
        if token.text in hlgwords:
            if doc[i+1].text in (hlgwords + vbgwords) or doc[i+1].like_num:
                span = [token.text]
                j = i+1
                while j < len(doc) and doc[j] in (hlgwords + vbgwords):
                    j = j +1
                temp = []
                for tok in span:
                    temp.append({"TEXT": tok})
                epatterns.append({"label": "Handlungsgrundlage",
                                  "pattern": temp})
    return epatterns

# This did not work as intended, made things worse (20240717):
# def match_datenfeld(doc, epatterns):
#     for i, token in enumerate(doc):
#         if (doc[i-3].text in ["Angaben","deren"]
#             and  doc[i-2].text in ["enthalten","Kenntnis"]
#             and doc[i-1].text in [":","1."]):
#             span = [token.text]
#             j = i+1
#             while j < len(doc) and doc[j] not in ["()"]:
#                 j = j+1
#             temp = []
#             for tok in span:
#                 temp.append({"TEXT": tok})
#             epatterns.append({"label": "Datenfeld",
#                               "pattern": temp})
#     return epatterns
           

def match_frist(doc, epatterns):
    # for token in doc:
    #     for i, token in enumerate(doc):
    #         if token.lemma_ == 'spätestens':
    #             if doc[i+1].text in ["mit", "bis", "jedoch"]:
    #                 subclause = [token.text]
    #                 j = i+1
    #                 while j < len(doc) and doc[j].text not in ['.']:
    #                     subclause.append(doc[j].text)
    #                     j = j + 1
    #                 temp = []
    #                 for tok in subclause:
    #                     temp.append({"TEXT": tok})
    #             epatterns.append({"label": "Frist", "pattern": temp})
    # Kernmuster: <Zahl> <Zeiteinheit>
    epatterns.append({"label": "Frist",
                      "pattern": [{"LIKE_NUM": True},
                                  {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                                    "Woche", "Monat", "Jahr"]}}]
                      })
    # mindestens ... lang
    epatterns.append({"label": "Frist",
                      "pattern": [{"TEXT": "mindestens"},
                                  {"LIKE_NUM": True},
                                  {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                                    "Woche", "Monat", "Jahr"]}},
                                  {"TEXT": "lang"}]
                      })
    # innerhalb einer Frist von ...
    epatterns.append({"label": "Frist",
                      "pattern": [{"LEMMA": "innerhalb"},
                                  {"TEXT": "einer"},
                                  {"LEMMA": "Frist"},
                                  {"LEMMA": "von"},
                                  {"LIKE_NUM": True},
                                  {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                                    "Woche", "Monat", "Jahr"]}}]
                      })
    # bis zu ...
    epatterns.append({"label": "Frist",
                      "pattern": [{"LEMMA": "bis"},
                                  {"LEMMA": "zu"},
                                  {"LIKE_NUM": True},
                                  {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                                    "Woche", "Monat", "Jahr"]}}]
                      })
    # ... vor Aufnahme der Tätigkeit
    epatterns.append({"label": "Frist",
                      "pattern": [{"LIKE_NUM": True},
                                  {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                                    "Woche", "Monat", "Jahr"]}},
                                  {"LEMMA": "vor"},
                                  {"LEMMA": "Aufnahme"},
                                  {"TEXT": "der"},
                                  {"LEMMA": "Tätigkeit"}]
                      })
    # nach ...
    epatterns.append({"label": "Frist",
                      "pattern": [{"LEMMA": "nach"},
                                  {"LIKE_NUM": True},
                                  {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                                    "Woche", "Monat", "Jahr"]}}]
                      })
    # innerhalb von ...
    epatterns.append({"label": "Frist",
                      "pattern": [{"LEMMA": "innerhalb"},
                                  {"LEMMA": "von"},
                                  {"LIKE_NUM": True},
                                  {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                                    "Woche", "Monat", "Jahr"]}}]
                      })
    # spätestens .... vor
    epatterns.append({"label": "Frist",
                      "pattern": [{"TEXT": "spätestens"},
                                  {"LIKE_NUM": True},
                                  {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                                    "Woche", "Monat", "Jahr"]}},
                                  {"LEMMA": "vor"}]
                      })
    return epatterns


