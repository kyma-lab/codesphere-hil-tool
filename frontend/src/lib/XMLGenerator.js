import { log } from "./CustomLogger";

	/**
	 * @param {number} min
	 * @param {number} max
	 */
	function getRandomInt(min, max) {
		// Using Math.floor() to round down and Math.random() to generate a random decimal between 0 and 1
		// The formula Math.floor(Math.random() * (max - min + 1)) + min will give you a random integer between min and max (both inclusive)
		return Math.floor(Math.random() * (max - min + 1)) + min;
	}




	/**
	 * @param {string[]} arr
	 */
	// returns the most frequent string in an array of strings
	function get_most_frequent_string(arr) {
		return arr
			.sort((/** @type {any} */ a, /** @type {any} */ b) => arr.filter((/** @type {any} */ v) => v === a).length - arr.filter((/** @type {any} */ v) => v === b).length)
			.pop();
	}




	// extracts all entities of a certain type from the list of entities, returns them in a list
	/**
	 * @param {any[]} entities_list
	 * @param {string} type
	 */
	export function extract_entities_of_type(entities_list, type) {
		let result = [];
		for (let i = 0; i < entities_list.length; i++) {
			if (entities_list[i][0] == type) {
				result.push(entities_list[i][1]);
			}
		}
		return result;
	}

	/**
	 * @param {string} actor
	 * @param {any[][]} input
	 */
	function add_row_for(actor, input) {

		// check if actor already exists
		for (let i = 0; i < input.length; i++) {
			if (input[i][0] == actor) {
				return i;
				
			}
		}

		// not found, add new row
		input.push([actor]);
		return input.length - 1;
	}


	// function that proccesses the annotated data and creates the input for the bpmn generator
	// iterates through entities in IOB, builds diagram layout
	/**
	 * @param {any[]} bpmnSourceInfo
	 */
	export function create_generator_input(bpmnSourceInfo) {
		//TODO : this input data structure is a mess, needs to be improved with custom classes
		//TODO : also improve the generate_bpmn thing, to expect a better input structure


		let result_receivers = extract_entities_of_type(bpmnSourceInfo, 'Ergebnisempfänger');
		let main_actors = extract_entities_of_type(bpmnSourceInfo, 'Hauptakteur');
		let actual_main_actor = get_most_frequent_string(main_actors);
		let actual_result_receiver = get_most_frequent_string(result_receivers);

		if (actual_main_actor == undefined) {
			actual_main_actor = 'Hauptakteur';
		}

		if (actual_result_receiver == undefined) {
			actual_result_receiver = 'Ergebnisempfänger';
		}

		let participants = extract_entities_of_type(bpmnSourceInfo, 'Mitwirkender');
		participants = [...new Set(participants)];

		log('XML_generator', 'actual_main_actor: ' + actual_main_actor);
		log('XML_generator', 'actual_result_receiver: ' + actual_result_receiver);
		log('XML_generator', 'participants: ' + participants);


		// main structure that will be built over time, returned at the end
		let input = [];

		// keep track of which index is what category
		let main_actor_row = null;
		let result_receiver_row = null;

		// mapping of participant names to their row index in the input array
		let participant_rows = [];

		for (let i = 0; i < bpmnSourceInfo.length; i++) {
			let tag_type = bpmnSourceInfo[i][0];
			let tag_content = bpmnSourceInfo[i][1];

			if (tag_type == 'Ergebnisempfänger') {
				if (tag_content == actual_result_receiver) {
					result_receiver_row = add_row_for(tag_content, input);
				}
			}
			if (tag_type == 'Hauptakteur') {
				if (tag_content == actual_main_actor) {
					main_actor_row = add_row_for(tag_content, input);

					// add this to the hauptakteur row by default, but only once
					// @ts-ignore
					input[main_actor_row].push(['MESSAGESTART', 'Antrag entgegennehmen', '']);
					// @ts-ignore
					input[main_actor_row].push(['Standard', 'Zust pruefen', '']);

				}
			}
			if (tag_type == 'Mitwirkender') {
				if (participants.includes(tag_content)) {
					let tmp = add_row_for(tag_content, input);
					participant_rows.push(tmp);
				}
			}
			if (tag_type == 'Handlungsgrundlage') {
					
			}
			if (tag_type == 'Aktion') {
				// add for random actor and in random order, Standard for now
				// keep a reference of the actor that was modified last

				if (input.length != 0) {
					let random_actor = getRandomInt(0, input.length - 1);
					let box_element = ['Standard', tag_content, ''];
					// @ts-ignore
					input[random_actor].push(box_element);

				}
			}
			if (tag_type == 'Signalwort') {
				// not handled yet
			}
			if (tag_type == 'Frist') {
				// not handled yet
			}
			if (tag_type == 'Bedingung') {
				// not handled yet
			}
			if (tag_type == 'Dokument') {
				// not handled yet
			}
			if (tag_type == 'Datenfeld') {
				// not handled yet
			}
		}

		//console.log('input:', input);
		log('XML_generator', 'returning generated template');
		return input;
	}