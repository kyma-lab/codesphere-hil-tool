import argparse
from pathlib import Path

##################################################################################
### THIS CAN BE USED AS A STANDALONE SCRIPT BUT IS ALSO INCLUDED IN predict.py
### IT LOADS A PROVIDED IOB2-file AND CREATES A STATIC .html FILE THAT VISUALIZES THE SENTENCES AND THEIR ANNOTATIONS
### NOTE: IT ONLY SUPPORTS A LIMITED NUMBER OF DIFFERENT CLASSES (UP TO 11 OR SOMETHING)
##################################################################################
## PROVIDE SOURCE AND TARGET PATH, INLCLUDING FILENAME AND ENDING
##################################################################################

def readLines(path):
    file2 = open(path, 'r')
    Lines = file2.readlines()
    file2.close()
    return Lines

def createTagColorDict(Lines):
    COLORS = ["#d43552", "#b854d4", "#6684e1", "#1fad83", "#60ac39", "#ae9513", "#b65611", "#F1C40F", "#a6a28c", "#4caf50", "#ff9800", "#01579b", "#ba68c8"]
    tagcolors = {}
    numSentences = 0
    # create dictionary containing all tags and their corresponding HEX color values (generate distinct colors automatically?)
    for line in Lines:
        if line == "\n" or line.strip() == "":
            numSentences += 1
        else:
            token = line.split(" ")
            if token[1] == "O\n":
                pass
            elif token[1] == "<unk>\n":
                pass
            else:
                tag = token[1].split("-")[1].strip()
                tagcolors[tag] = "undefined"

    i = 0
    for key in tagcolors.keys():
        tagcolors[key] = COLORS[i]
        i = i + 1
    return numSentences, tagcolors

def startHTMLtemplate(file1, pathOutput, numSentences, tagcolors):
    # start HTML template, add header, legend

    file1.writelines('<!DOCTYPE html> \n <body> \n <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">')

    file1.writelines('<div class="container" style="color:black;">')
    file1.writelines('<div class="row">')
    file1.writelines('<div class="col-8">')

    file1.writelines("<h3 style='margin-top: 50px'> <span style='font-size:70%'>currently viewing:</span> " + str(pathOutput) + "</h3>")
    file1.writelines("<p> containing " + str(numSentences) + " sentences </p>")
    file1.writelines("<p> containing " + str(len(tagcolors.keys())) + " distinct classes </p>")
    file1.writelines("<p> legend:  ")

    for key in tagcolors.keys():
        file1.writelines("<span style='background-color:" + tagcolors[key] + "'> " + key +" </span>")
    file1.writelines("</p>")
    file1.writelines("<hr>")

def spawnSentences(file1, Lines, tagcolors):
    count = 0
    file1.writelines("<h5> sentence no°" + str(count) + "</h5>")
    file1.writelines("<p style='line-height:1.4'>")
    count = count + 1

    previousTag = ""
    currentTag = "x"

    for line in Lines:
        if line == "\n":
            #new sentence starts
            file1.writelines("<hr>")
            file1.writelines("</p><h5> sentence no°" + str(count) + "</h5><p style='line-height:2'>")
            count = count + 1
        else:
            token= line.split(" ")
            if token[1] == "O\n" or token[1] == "<unk>\n":
                #token is not part of an entity
                previousTag = currentTag
                currentTag = "O"
                if previousTag != currentTag:
                    #previous entity ends, close span
                    file1.write("</span> "+line.split(" ")[0] + " ")
                else:
                    #previous token was also class O, no span to be closed, just print text
                    file1.write(" " + line.split(" ")[0] + " ")
            else:
                #old sentence continues
                group = token[1].split("-")[1].strip()
                previousTag = currentTag
                currentTag = group
                if currentTag == previousTag:
                    #old span continues (multi-token-entity)
                    file1.write(token[0] + " ")
                else:
                    #old span has to be closed, new entity starts
                    color = tagcolors[currentTag]
                    file1.write('</span>')
                    infoSpan = '<span style="position:relative;bottom:3px;font-size:50%; background-color:white; color:'+ color +'; border-radius: 25px; padding: 5px; margin: 5px">' + currentTag + ' </span>'
                    file1.write('<span style="background-color:' + color + '; border-radius: 25px; padding: 5px; margin: 5px">'+ infoSpan + token[0] + ' ')

def endHTMLtemplate(file1):
    # end HTML template
    file1.writelines('</p> </div>')
    file1.writelines('</div>')
    file1.writelines('</div')
    file1.writelines('</div>')
    file1.writelines("\n</body> </html>")
    file1.close()

def visualize(path, pathOut):
    Lines = readLines(path)
    numSentences, tagcolors = createTagColorDict(Lines)
    file1 = open(pathOut, 'w')
    startHTMLtemplate(file1, pathOut, numSentences, tagcolors)
    spawnSentences(file1, Lines, tagcolors)
    endHTMLtemplate(file1)
    file1.close()

def main():

    parser = argparse.ArgumentParser(usage="provide with two paths, first has to lead to a .txt in IOB2 format, second ist the ouput file .html which will be created\ne.g. python3 visuals.py datasets/train.txt ./demo.html",
                                    description="creates a static .html document visualizing the sentences and their annotations")

    parser.add_argument("source_file")
    parser.add_argument("target_file")
    args = parser.parse_args()
    dirA = Path(args.source_file)
    dirB = Path(args.target_file)

    if not dirA.exists():
        print("source file doesn't exist")
        raise SystemExit(1)

    visualize(dirA, dirB)

if __name__ == "__main__":
    main()