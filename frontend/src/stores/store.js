// store.js
import AnnotatedFiles from '$lib/AnnotatedFiles';
import { writable } from 'svelte/store';

export const annotationIntake = writable(new AnnotatedFiles([]));

export const processIntake = writable(new AnnotatedFiles([]));

export const modifiedAnnotations = writable('Initial Value');

export const jwt = writable();

export const search_parameters = writable({'search_query': '', 'search_type': 'init'});

export const search_selection = writable([]);