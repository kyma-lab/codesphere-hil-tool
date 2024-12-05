import DocumentContainer from "$lib/DocumentContainer.js";
import { log } from "./CustomLogger";
import { AuthorizationError } from "./Errors";



const apiUrl = import.meta.env.VITE_SERVER_HOST_LOCATION;

/**
 * @param {string | number | boolean} searchQuery
 * @param {any} token
 */
export async function search_request(searchQuery, token) {

    try {
        const response = await fetch(
            apiUrl + `/api/search/?query=${encodeURIComponent(searchQuery)}`,
            {
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                }
            }
        );
        log('API', 'Search (normal) request sent');
        const data = await response.json();

        if (response.status !== 200) {
            throw new Error('Failed to fetch data from the backend');
        }

        return {
            data: data,
            status: response.status
        }


    } catch (error) {
        console.error('Failed to fetch data from the backend:', error);

        return {
            data: null,
            status: 500
        }
    }
}

/**
 * @param {string | number | boolean} searchQuery
 * @param {any} token
 */
export async function semantic_search_request(searchQuery, token) {
    try {
        const response = await fetch(
            apiUrl + `/api/search_semantic/?query=${encodeURIComponent(searchQuery)}`,
            {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
        );
        log('API', 'Search (semantic) request sent');
        const data = await response.json();

        if (response.status !== 200) {
            throw new Error('Failed to fetch data from the backend');
        }

        return {
            data: data,
            status: response.status
        }

    } catch (error) {
        console.error('Failed to fetch data from the backend:', error);

        return {
            data: null,
            status: 500
        }
    }
}



// for sending selected search results to the backend, then proceed with annotation view
// performs pdf processing etc
/**
 * @param {{ files: DocumentContainer[]; method: string; }} json
 * @param {string} token
 */
export async function send_selected_to_intake(json, token) {

    try {
        const url = apiUrl + '/api/getpredictions';
        const contentType = 'application/json';

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': contentType,
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(json)
            });
            const data = await response.json();
            return {
                data: data,
                status: response.status
            };
        } catch (error) {
            console.error('Error:', error);
            return {
                data: null,
                status: 500
            };
        }
    } catch (error) {
        return {
            data: null,
            status: 500
        }
    }
}


/**
 * @param {{ files: DocumentContainer[]; }} files
 * @param {string} token
 */
export async function send_to_database(files, token) {

    try {
        const response = await fetch(apiUrl + '/api/contribute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(files)
        });

        log('API', 'Contribution request sent');

        if (!response.ok) {

            console.error('Failed to send data to the backend:', response);
            return {
                data: null,
                status: 500
            }
        } else {
            const data = await response.json();
            return {
                data: data,
                status: response.status
            }
        }

    } catch (error) {
        return {
            data: null,
            status: 500
        }
    }
}


/**
 * @param {string} token
 * @param {string} username
 * @param {string} new_password
 */
export async function change_password(username, token, new_password) {
    try {
        const response = await fetch(apiUrl + '/api/change_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({username: username, password: new_password})
        });

        if (!response.ok) {

            console.error('Failed to send data to the backend:', response);
            return {
                data: null,
                status: 500
            }
        } else {
            const data = await response.json();
            return {
                data: data,
                status: response.status
            }
        }

    } catch (error) {
        return {
            data: null,
            status: 500
        }
    }
}

/**
 * @param {string} token
 * @param {string} username
 * @param {string} password
 */
export async function db_add_user(token, username, password) {
    try {
        const response = await fetch(apiUrl + '/api/add_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            console.error('Failed to send data to the backend:', response);
            return {
                data: null,
                status: 500
            }
        } else {
            const data = await response.json();
            return {
                data: data,
                status: response.status
            }
        }

        
    } catch (error) {
        console.error('Registration failed 02');

        return {
            data: null,
            status: 500
        }
    }

}


/**
 * @param {string} username
 * @param {string} bpmn_xml
 * @param {string} token
 */
export async function db_store_bpmn(bpmn_xml, username, token) {
    try {
        const response = await fetch(apiUrl + '/api/bpmn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ username, bpmn_xml})
        });

        if (!response.ok) {
            console.error('Failed to send xml-data to the backend:', response);
            return {
                data: null,
                status: 500
            }
        } else {
            const data = await response.json();
            return {
                data: data,
                status: response.status
            }
        }

        
    } catch (error) {
        console.error('BPMN storage failed 02');

        return {
            data: null,
            status: 500
        }
    }

}


/**
 * @param {string} token
 */
export async function db_logout(token) {
    // post request to the /api/logout endpoint without any payload
    try {
        const response = await fetch(apiUrl + '/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            }
        });

        if (!response.ok) {
            console.error('Logout failed 02', response);
            return {
                data: null,
                status: 500
            }
        } else {
            const data = await response.json();
            return {
                data: data,
                status: response.status
            }
        }

        
    } catch (error) {
        console.error('Logout failed 03');

        return {
            data: null,
            status: 500
        }
    }
}


/**
 * Fetches the system health status from the API.
 *
 * This function sends a GET request to the `/api/health` endpoint to check the system's health status.
 * It returns an object containing the response data and status code.
 * The response data contains the health status for various components as dictionary.
 *
 * @async
 * @function get_system_health
 * @returns {Promise<Object>} An object containing the response data and status code.
 * @property {Object|null} data - The response data from the API, or null if the request failed.
 * @property {number} status - The HTTP status code of the response.
 */
export async function get_system_health() {
    // post request to the /api/logout endpoint without any payload
    try {
        const response = await fetch(apiUrl + '/api/health', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Healthcheck failed 02', response);
            return {
                data: null,
                status: 500
            }
        } else {
            const data = await response.json();
            return {
                data: data,
                status: response.status
            }
        }

        
    } catch (error) {
        console.error('Healthcheck failed 03', error);

        return {
            data: null,
            status: 500
        }
    }
}



/**
 * @param {string} username
 * @param {string} password
 */
export async function db_login(username, password) {

    const response = await fetch(apiUrl + '/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
        if (response.status === 401) {
            console.error('Authentication failed');
            throw new AuthorizationError('Authentication failed');
        } else {
            console.error('Server error');
            throw new Error('Server error');
        }
    } else {
        const data = await response.json();
        return data.access_token;
    }
    


}