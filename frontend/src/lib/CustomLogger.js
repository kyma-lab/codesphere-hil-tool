


let LOGGING_ENABLED = true;

/**
 * @param {string} tag
 * @param {string} text
 */
export function log(tag, text) {
    if (!LOGGING_ENABLED) return;

    const logEntry = {
        timestamp: new Date().toISOString(),
        tag: tag,
        text: text
    };

    console.log(logEntry);
}
