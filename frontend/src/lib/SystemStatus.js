import { get_system_health } from "./API";

/**
 * Class representing the system status.
 */
export class SystemStatus {
    /**
     * Create a SystemStatus instance.
     */
    constructor() {
        /**
         * The status of various system components.
         * @property {Object} status 
         * @property {string} status.predictor
         * @property {string} status.trainer 
         * @property {string} status.bilstm-crf
         * @property {string} status.xlm-r
         */
        this.status = {
            "predictor": "Unavailable",
            "trainer": "Unavailable",
            "bilstm-crf": "Unavailable",
            "xlm-r": "Unavailable"
        };
    }

    /**
     * Update the system status by fetching the latest health data.
     * @async
     * @returns {Promise<void>}
     */
    async update() {
        let systemHealth = await get_system_health();

        if (systemHealth.status != 200) {
            return;
        }

        this.status = systemHealth.data.system_status;
        console.log("System status updated: ", this.status);
    }
    /**
     * Get the status of the predictor component.
     * @returns {string} The status of the predictor component.     
     */
    get predictor() {
        return this.status["predictor"];
    }

    /**
     * Get the status of the trainer component.     
     * @returns {string} The status of the trainer component.     
     */
    get trainer() {
        return this.status["trainer"];
    }

    /** 
     * Get the status of the bilstm-crf component.     
     * @returns {string} The status of the bilstm-crf component.    
     */
    get bilstm_crf() {
        return this.status["bilstm-crf"];
    }

    /** 
     * Get the status of the xlm-r component.     
     * @returns {string} The status of the xlm-r component.    
     */
    get xlm_r() {
        return this.status["xlm-r"];
    }
}