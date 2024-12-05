# -*- coding: utf-8 -*-
import argparse
from pathlib import Path
import os
import regex

##################################################################################
# can be used as standalone script to check iob file formatting
# checks compliance with tagging rules (I only after B with same class, or O tags)
# checks format (2 elements per line)
# lists all occuring classes
# ! modified version that checks entire folder
##################################################################################


def validateIOB_Testset(data):
    # for testsets, we only check the format (1 element per line, which is the text)
    lines = data.split("\n")
    violation_counter = 0
    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if line:
            parts = line.split(" ")
            if len(parts) != 1:
                print(f"Error in line {line_number}: Invalid format (invalid number of elements in line: {parts})")
                violation_counter += 1
                continue
    
    if violation_counter == 0:
        return 0
    else:
        return violation_counter


def validateIOB(data, count, tab_separated):
    # expects IOB document as single string
    lines = data.split("\n")
    violation_counter = 0
    previous_label = "O"
    classes = []

    for line_number, line in enumerate(lines, start=1):

        line_unicodes = []
        for char in line:
            unicode_code = ord(char)
            uni_string = f"\\u{unicode_code:04x}"
            line_unicodes.append(uni_string)

        line = line.strip()

        if line:
            if tab_separated:
                parts = line.split("\t")
            else:
                parts = line.split(" ")

            if len(parts) != 2:
                print(f"Error in line {line_number}: Invalid format (too many elements in line: {parts})")

                print(line_unicodes)

                if count:
                    violation_counter += 1
                    continue
                else:
                    print("Aborting.")
                    return False

            text, label = parts[0], parts[1]

            if label == "O":
                previous_label = label

            elif label.startswith("B-"):
                # i think this is always correct, no matter the class and the location?!
                cls = label.split("-")[1]
                classes.append(cls)
                # for tracking the classes that appear in the document
                previous_label = label
                # reset current "working" class
                pass

            elif label.startswith("I-"):
                if not previous_label.startswith(("B-", "I-")):
                    print(f"Error in line {line_number}: Invalid IOB2 seq (use of I-tag without preceeding B- or I-tag)")
                    # should also check if the correct class is
                    # used in continuation of I-

                    if count:
                        violation_counter += 1
                        continue
                    else:
                        print("Aborting.")
                        return False

                if previous_label.split("-")[1] != label.split("-")[1]:
                    print(f"Error in line {line_number}: Invalid IOB2 seq (class changed mid-annotation)")

                    if count:
                        violation_counter += 1
                        continue
                    else:
                        print("Aborting.")
                        return False
            else:
                # invalid label error (only B-, I- and O labels are allowed)
                print(f"Error in line {line_number}: Invalid label: {label}")
                if count:
                    violation_counter += 1
                    continue
                else:
                    print("Aborting.")
                    return False



    #print("=========================================")
    #print("========== DATASET INFORMATION ==========")
    #print("=========================================")
    #print("#tokens: ", len(lines))
    #print("#classes: (#unique tags): " + str(len(set(classes))))
    #print("classes: ", set(classes))

    if count:
        return violation_counter
    else:
        return True


def validate_file_title_format(file_titles):
    for title in file_titles:
        if len(title) > 200:
            return False
    return True


def validate_file_content_format(file_contents):
    for content in file_contents:
        if not isinstance(content, str):
            return False
        if len(content) > 10000:
            return False
    return True

def validate_input(input_string):

    if not isinstance(input_string, str):
        return False
    
    if len(input_string) < 4:
        return False
    
    if len(input_string) > 20:
        return False
    
    # make sure it only contains letters and numbers
    if not regex.match("^[a-zA-Z0-9]*$", input_string):
        return False

    return True


def main():

    # -------- checking input & loading dataset below this line --------
    parser = argparse.ArgumentParser(usage="provide with path to one or more files, e.g. train.txt\ne.g. python3 tool_validate.py somefolder",
                                description="checks if files in provided folder comply with iob format, lists all used classes, otherwise hints at possible violation")

    parser.add_argument("path")
    parser.add_argument('-t', action='store_true', help='tab separation instead of whitespace')
    parser.add_argument('-c', action='store_true', help='counts validations, doesnt stop after finding one error, returns count')
    parser.add_argument('-v', action='store_true', help='prints each line from the IOB document before validating it')


    args = parser.parse_args()

    target_path = Path(args.path)
    count = args.c
    verbose = args.v
    tab_separated = args.t

    print("WARNING: THIS SCRIPT IS NOT FULLY CORRECT. BETTER USE seqscore library!")
    print("WARNING: THIS SCRIPT IS NOT FULLY CORRECT. BETTER USE seqscore library!")
    print("WARNING: THIS SCRIPT IS NOT FULLY CORRECT. BETTER USE seqscore library!")


    if not target_path.exists():
        print("The target directory doesn't exist")
        raise SystemExit(1)

    global_count = 0
    for file_path in os.listdir(args.path):

        file = open(os.path.join(args.path,file_path), "r")
        #print("Opening file at path: ", file_path)

        data = file.read()
        violation_counter = validateIOB(data, count, verbose, tab_separated)
        global_count += violation_counter

    print("Global error count:", global_count)

if __name__ == "__main__":
    main()
