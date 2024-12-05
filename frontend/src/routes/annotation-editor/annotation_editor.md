# Frontend - Annotation Editor

## Code Structure

The code for the annotation editor is located here: `frontend/src/routes/annotation-editor/+page.svelte`
The code is not written in an object-oriented fashion, and instead relies on functions to manage state that is stored in global variables.
The functions are used to handle user input.

As it is required by Svelte, the `.svelte` file consists of three parts:
- JavaScript section
- HTML section
- CSS section 


### JavaScript

- the script section starts by importing various modules and components needed for the functionality, including store data and fontAwesome icons.

```
	import { dataStore, iobForBPMN } from '../../stores/store.js';
    ...
	import { goto } from '$app/navigation';
```

- it defines helper functions like,
    1. **<em>convertIOBToAnnotations<em>**
    2. **<em>handleSelectionChange<em>**
    3. **<em>applyAnnotation<em>**
    4. **<em>handleAnnotationClick<em>**
    5. **<em>handleDelete<em>**
    6. **<em>unDoAction<em>**
    7. **<em>convertJsonToIOB<em>**
    8. **<em>sendToProcessView<em>**
    9. **<em>sendToBackend<em>**


- it initializes and manages states such as annotatedData, currentIndex, showPopup, words, annotationsForWords, filteredAnnotations, and isLoading.

- the script handles user interactions like selecting text for applying annotations, modifying the exisiting annotations, deleting the annotations that are not predicted incorrect by the model, navigating through data, handling the history of changes, and sending data to the backend and to the process view.

#### Function Explanations

### `convertIOBToAnnotationsJson(iobText)`
This function takes in an IOB formatted **text** with **Annotations** and converts it into suitable JSON data structure with their corresponding text range to make it easy to display on the front-end. It parses the IOB text, extracts annotations, and returns an object containing annotations, text range, and an empty history key to store the history of changes in the furtue.

### `handleSelectionChange()`
Handles the change in text selection by the user which meand whenver the user selection starts and ends. It checks for overlaps with existing annotations and adjusts the position of the popup accordingly.

### `applyAnnotation(annotationLabel)`
Applies the annotation with the provided label to the selected text. It updates the annotated data, history, and recalculates annotations for words.

### `handleAnnotationClick(event)`
Handles click events on the existing annottaions on the front-end. It retrieves information about the clicked annotation and prepares the popup for modification.

### `handleDelete()`
Handles the deletion of annotations. It removes the selected annotation from the annotated data and recalculates annotations for words.

### `unDoAction(annotation)`
Undoes the action performed on the annotation, whether it's adding, modifying, or deleting. It updates the annotated data accordingly.

### `convertJsonToIOB(data)`
As the changes are stored in the JSON data structure, it Converts annotations in JSON format to IOB format. It constructs IOB tags for each word based on the provided annotations.

### `sendToProcessView()`
Sends the annotated data to the backend for further processing. It converts the data to IOB format, sends it to the backend API, and redirects to the process view.

### `sendToBackend(iobString)`
Sends the IOB formatted data to the backend API for processing. It constructs the data payload, makes a POST request to the backend, and returns the response.


#### Integration:

- event handlers like **<em>on:click<em>**, **<em>on:mouseup<em>**, and **<em>on:change<em>** are used to trigger JavaScript functions based on user actions.
data binding **<em>(bind:value)<em>** is utilized to synchronize input values with JavaScript variables.
conditional rendering **(#if blocks)** is employed to show or hide elements based on certain conditions.

#### asynchronous operations:

- the code handles asynchronous operations such as fetching data from a backend API using fetch and await, and it utilizes loading indicators (isLoading) to provide feedback to the user during these operations.

### CSS

Global CSS is used where possible. If necessary, custom CSS classes are defined and used. 
For dynamic and conditional styling inline-styles are used, when introducing separate classes would add unreasonable overhead.

### Diagram

 ![Landing Page Architecture](../../../../resources/graphics/annotation_editor.jpg)

## Inspiration and Reference

The Inception tool, developed by Technische Universität Darmstadt, served as a valuable resource in understanding the procedures involved. By exploring the features and capabilities of the Inception tool, we were able to glean valuable insights and formulate a structured approach to the task at hand. This included analyzing its user interface, studying its documentation, and experimenting with its various functionalities to grasp the underlying principles.