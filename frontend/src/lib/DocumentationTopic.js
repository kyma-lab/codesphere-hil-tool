
export default class DocumentationTopic {
    /**
     * @param {string} title
     * @param {string} content
     * @param {string[]} steps
     */
    constructor(title, content,  steps) {
        this.title = title;
        this.content = content;
        this.steps = steps;
    }

    get_title() {
        return this.title;
    }

    get_content() {
        return this.content;
    }

    get_steps() {
        return this.steps;
    }

    to_json() {
        return JSON.stringify({
            title: this.title,
            content: this.content
        }, null, 2);
    }
}

