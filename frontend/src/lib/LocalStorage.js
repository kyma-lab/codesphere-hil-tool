import { log } from "./CustomLogger";

	/**
	 * @param {string} key
	 */
	export function retrieveFromLocalStorage(key) {
		if (typeof localStorage !== 'undefined') {
			let checkpoint = localStorage.getItem(key);
			if (checkpoint) {
				log('LocalStorage', 'Retrieved key:' + key + ' from storage');
				return checkpoint;
			} else {
				log('LocalStorage', 'Requested key:' + key + ' not found in local storage.');
			}
		}
	}

	/**
	 * @param {string} key
	 * @param {string} value
	 */
	export async function saveToLocalStorage(key, value) {
		if (typeof localStorage !== 'undefined') {
			try {
				localStorage.setItem(key, value);
				log('LocalStorage', 'Saved key:' + key + ' to storage');
			} catch (err) {
				console.error('Error saving to local storage:', err);
			}
		}
	}