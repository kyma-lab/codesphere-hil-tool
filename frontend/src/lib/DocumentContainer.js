// src/lib/MyClass.js
export default class DocumentContainer {
    /**
     * @param {string} title
     * @param {string} content
     */

    constructor(title, content) {
        this.title = title;
        this.content = content;
    }

    is_empty() {
        return this.content === '';
    }

    /**
     * @param {string[]} titles
     * @param {string[]} contents
     */
    static build_array(titles, contents) {

        if (titles.length !== contents.length) {
            throw new Error("Title and content arrays must have the same length");
        }

        /**
         * @param {DocumentContainer[]} files
         */
        let files = [];
        for (let i = 0; i < titles.length; i++) {
            files.push(new DocumentContainer(titles[i], contents[i]));
        }
        return files;
    }


}   