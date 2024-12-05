/**
 * returns a list of strings, where each string is a document with IOB tags
 * @param {any[]} data
 */
export function convertJsonToIOB(data) {
    return data.map((item) => {
        const text = item.text;
        const annotations = item.annotations;
        let iobTags = new Array(text.length).fill('O');

        annotations.forEach(
            (/** @type {{ label: any; start_word_index: any; end_word_index: any; }} */ annotation) => {
                const { label, start_word_index, end_word_index } = annotation;
                const startIndex = start_word_index - 1; // Adjust for one-based index
                const endIndex = end_word_index - 1; // Adjust for one-based index

                iobTags[startIndex] = `B-${label}`;
                for (let i = startIndex + 1; i <= endIndex; i++) {
                    iobTags[i] = `I-${label}`;
                }
            }
        );

        // Constructing the output
        // @ts-nocheck
        const formattedData = text.map((/** @type {any} */ word, /** @type {any} */ index) => ({
            word,
            tag: iobTags[index]
        }));
        const formattedString = formattedData.map(
            (/** @type {{ word: any; tag: any; }} */ item) => `${item.word} ${item.tag}`
        );

        // list of strings, 1 element in list = 1 file with iob
        return formattedString.join('\n');
    });
}

/**
* @param {string} iobText
*/
export function convertIOBToAnnotationsJson(iobText) {
    const annotations = [];
    const lines = iobText
        .trim()
        .split('\n')
        .filter((line) => line.trim() !== '');
    const text = [];

    let currentAnnotation = null;
    let currentTag = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        const words = line.trim().split(' ');

        if (words.length > 1) {
            const firstWord = words[0];
            text.push(firstWord);

            const secondWord = words[1];

            if (secondWord.startsWith('B-')) {
                if (currentAnnotation !== null) {
                    annotations.push(currentAnnotation);
                }

                currentTag = secondWord.split('-')[1];
                currentAnnotation = {
                    start_word_index: i + 1,
                    end_word_index: i + 1,
                    label: currentTag
                };
            } else if (secondWord === `I-${currentTag}` && currentAnnotation !== null) {
                currentAnnotation.end_word_index = i + 1;
            } else {
                if (currentAnnotation !== null) {
                    annotations.push(currentAnnotation);
                    currentAnnotation = null;
                }
                currentTag = null;
            }
        }
    }

    if (currentAnnotation !== null) {
        annotations.push(currentAnnotation);
    }

    return { annotations: annotations, text: text, history: [] };
}