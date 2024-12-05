import DocumentContainer from "./DocumentContainer.js";

// src/lib/MyClass.js
export default class AnnotatedFiles {
    /**
     * @param {DocumentContainer[]} files
     */
    constructor(files) {
        this.files = files;
    }

    get_files() {
        return this.files;
    }

    to_json() {
        return JSON.stringify(this.files, null, 0);
    }

    /**
     * @param {number} index
     */
    get_file(index) {

        return this.files[index];
    }

    get_length() {
        return this.files.length;
    }

    is_empty() {
        return this.files.length == 0;
    }

    get_titles() {
        return this.files.map(file => file.title);
    }

    get_contents() {
        if (this.is_empty()) {
            return [];
        }

        return this.files.map(file => file.content);
    }

    /**
     * @param {string} json
     */
    static from_json(json) {
        try {
            return new AnnotatedFiles(JSON.parse(json));
        } catch (error) {
            console.error("Invalid JSON string", error);
            return new AnnotatedFiles([]);
        }
    }
}