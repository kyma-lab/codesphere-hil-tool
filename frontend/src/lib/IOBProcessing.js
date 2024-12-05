	/**
	 * @param {string} input_string_iob
	 */
	// returns a list of pairs of (entity content, entity type) in the order that they occur in the IOB
	export function extract_entities(input_string_iob) {
		if (input_string_iob === '') {
			return [];
		}

		let allLines = input_string_iob.split('\n');
		let workingEntity = '';
		let workingEntityType = '';
		let firstPush = true;
		let entities = [];

		allLines.forEach((/** @type {string} */ line) => {
			if (line === '') {
				return;
			}
			let thing = line.split(' ');
			let word = thing[0];
			let tag = thing[1];

			if (tag !== 'O') {
				if (tag.includes('B-')) {
					if (firstPush == true) {
						firstPush = false;
					} else {
						entities.push([workingEntityType, workingEntity]);
					}

					workingEntity = word;
					workingEntityType = tag.split('-')[1];
				}
				if (tag.includes('I-')) {
					if (workingEntityType === tag.split('-')[1]) {
						workingEntity += ' ' + word;
					}
				}
			}
		});

		if (workingEntity !== '') {
			entities.push([workingEntityType, workingEntity]);
		}

		return entities;
	}

