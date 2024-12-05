export class AuthorizationError extends Error {
    /**
     * @param {string | undefined} message
     */
    constructor(message) {
        super(message);
        this.name = "AuthorizationError";
    }
}