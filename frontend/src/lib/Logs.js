export class LogEntry {
    /**
     * @param {string} timestamp
     * @param {string} level
     * @param {string} message
     */
    constructor(timestamp, level, message) {
        this.timestamp = timestamp;
        this.level = level;
        this.message = message;
    }
}

export class LogContainer {
    /**
     * @param {LogEntry[]} server
     * @param {LogEntry[]} trainer
     * @param {LogEntry[]} predictor
     */
    constructor(server, trainer, predictor) {
        this.server = server;
        this.trainer = trainer;
        this.predictor = predictor;
    }

    /**
     * @param {string} source
     */
    getBySource(source) {
        switch (source) {
            case 'server':
                return this.server;
            case 'trainer':
                return this.trainer;
            case 'predictor':
                return this.predictor;
            default:
                return [];
        }
    }
}