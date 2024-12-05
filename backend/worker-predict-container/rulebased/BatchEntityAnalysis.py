"""Batch processing all files in a folder"""
import os
import spacy
from pathlib import Path, PurePath
from entities_for_norms import EntitiesForNorms
from Frist import Frist
from Aktion import Aktion
from Signalwort import Signalwort
from Handlungsgrundlage import Handlungsgrundlage
from Hauptakteur import Hauptakteur
from Ergebnisempfaenger import Ergebnisempfaenger
from Mitwirkender import Mitwirkender
from Dokument import Dokument
from Datenfeld import Datenfeld
import argparse
from shared.config import BASE_TMP_PATH




def predictWithRules(uuid: str, input_path: str):
    print("Predicting with rules")
    print("received path: ", input_path)

    config = {
        "validate": False,
        "overwrite_ents": True,
    }

    # generate temporary output path
    tmp_folder = Path(f"{uuid}/persentence/")
    outputfolder = Path(f"{uuid}/persentence_pred/")

    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)

    input_path += "/test.txt"
    

    # print the current directory
    print("Current directory: ", os.getcwd())

    split_single_file_into_sentences(input_path, tmp_folder)

    # Disable SpaCy's own NER to replace it with our EntityRuler.
    # Since we don't use dependency relations in the present setup,
    # we disable the (dependency) parser as well. But this may change.

    thenlp = spacy.load("de_core_news_sm", disable=["ner", "parser"])
    theruler = thenlp.add_pipe("entity_ruler", config=config, after="lemmatizer")
    # modularising patterns into class attributes
    getspat = (Signalwort.d + Aktion.d + Hauptakteur.d + Handlungsgrundlage.d + Frist.d 
            + Ergebnisempfaenger.d + Mitwirkender.d + Datenfeld.d + Dokument.d)

    # add_patterns can only applied once to theruler,
    # therefore we have to construct one variable holding all patterns: getspat
    thespat = theruler.from_disk("patternlists/patterns.jsonl").add_patterns(getspat)

    inputfolder = str(tmp_folder)
    outputfolder = str(outputfolder)

    print("Patterns added to EntityRuler")
    print("Processing files...")

    # sort by file number (e.g. 0, 1, 2, 3, ...) assigned in split_single_file_into_sentences
    files = sorted(os.listdir(inputfolder), key=lambda x: int(os.path.splitext(x)[0]))

    for file in files:
        ea = EntitiesForNorms(
            inputfolder + os.sep + file,
            thenlp,
            theruler,
            thespat)
        ea.predict()
        outfile = str(outputfolder) + os.sep + file
        ea.to_file(outfile)
        print(f"File {file} processed and written to {outfile}")


    # re-combine the files into one string, then return it
    files = sorted(os.listdir(outputfolder), key=lambda x: int(os.path.splitext(x)[0]))

    output_string = ""
    for file in files:
        print("Reading file: ", file)
        with open(outputfolder + os.sep + file) as infile:
            output_string += infile.read() + "\n\n"

    print("Output string: ", output_string)

    # remove the temporary input folder (non-annotated files per sentence)
    for file in os.listdir(inputfolder):
        os.remove(inputfolder + os.sep + file)
    os.rmdir(inputfolder)


    # remove the temporary output folder (annotated files per sentence)
    for file in os.listdir(outputfolder):
        os.remove(outputfolder + os.sep + file)
    os.rmdir(outputfolder)


    # remove the temporary input folder (single files)
    for file in os.listdir(input_path[:-8]):
        os.remove(input_path[:-8] + os.sep + file)
    os.rmdir(input_path[:-8])


    return output_string



def split_single_file_into_sentences(file_path, output_dir):
    """
    Splits a single IOB file into sentences and writes each sentence in IOB format into a separate file.

    Args:
        file_path (str): The path to the input file.
        output_dir (str): The directory where the output files will be written.

    Returns:
        str: The path to the output directory.

    """
    print("Input file: ", file_path)
    with open(file_path, 'r') as f:
        print("Reading file...", file_path)
        lines = f.readlines()
        
        # split this array into a list of sentences, at the empty lines
        lines = "".join(lines).split("\n\n")

        # write each line into a separate file
        for i, line in enumerate(lines):
            with open(str(output_dir) + "/" + str(i), 'w') as f:
                f.write(line)
    
    print("Splitting done")
    print("Output directory: ", output_dir.absolute())
    return output_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("uuid", help="UUID parameter")
    parser.add_argument("input_path", help="Input path parameter")
    args = parser.parse_args()

    results = predictWithRules(args.uuid, args.input_path)
    print(results)

