# EntityRuler patterns

EntityRuler patterns as used in this system 
are Python dictionaries as follows: 

```
{"label": "Entity A", "pattern": [... list of token patterns ...]}
```
SpaCy has functionality to write these patterns to disk in JSONL format, 
and to read patterns from JSONL files on disk. 
The patterns for Handlungsgrundlage and Hauptakteur are saved 
in the `patterns.jsonl` file in this directory. 
See the main REAMDE.md for details on how this file is created. 

See the SpacY documentation for details about the format of the patterns: 
https://spacy.io/usage/rule-based-matching#entityruler



# Definition of patterns specific for administrative processes

The patterns for matching the following entities are defined as follows:


| NE                 | pattern                                                                                     |
|--------------------|---------------------------------------------------------------------------------------------|
| Aktion             | A word ending in "-ung" or a verb in "zu-" infinitive VVIZU                                 |
| Bedingung          | Subordinate clause introduced by "wenn" or a clause with a finite verb in initial position. |
| Signalwort         | Modal verb in finite form, tagged as VMFIN                                                  |
| Ergebnisempfänger  | Token text is "derjenige"                                                                   |
| Handlungsgrundlage | Token is tagged as GS (flair)                                                               |
| Hauptakteur        | Token is tagged as INN (flair)                                                              |
| Frist              | Sequence of <Zahl> <Zeiteinheit> optionally with temporal modifiers (see documents below).  |



The rational for defining these patterns in this way 
is described in the document 
https://fusion.gitpages.uni-jena.de/project/ozg/04_ergebnisse/00-canareno/Meilenstein_1/Forschungsergebnisse/Datenexploration

See also 
https://git.uni-jena.de/fusion/project/ozg/01_working/canareno-project/annotation_guidelines


















