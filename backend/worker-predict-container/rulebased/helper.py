import os


def read_file(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    # if not file_path.endswith('.txt'):
    #     raise ValueError(f"File '{file_path}' is not a .txt file.")

    with open(file_path, 'r', encoding="utf-8") as file:
        file_content = file.read()
        return file_content

def read_file_as_lines(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    if not file_path.endswith('.txt'):
        raise ValueError(f"File '{file_path}' is not a .txt file.")

    with open(file_path, 'r', encoding="utf-8") as file:
        file_content = file.readlines()
        return file_content


def add_wordlist(matcher, wordlist, tag):
    for word in wordlist:
        temp = []
        temp.append({"TEXT": word})
        pat = (tag, [temp])
        if pat not in matcher:
            matcher.append(pat)
    return matcher
