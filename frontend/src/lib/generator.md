# Documentation for BPMN Generation 

## Intro

We are using the bpmn.io Editor in our tool for users to create and modify bpmn diagrams.
BPMN is stored in XML.
To generate templates or suggestions for graphs and to be able to display them in the editor, these suggestions have to be in the BPMN format too.
It is impractical to directly generate the BPMN XML file itself.
Instead, we can create an intermediate representation of the graph, with less degrees of freedom.

For this, I already create an initial version (which is bad).

Currently, the `bpmn_generator.js` script can take in the following object:

```
let input = [
    [
        'PartyA', ['Standard', 'FirstTaskFirstBox', 'AnnotationText']
    ],
    [
        'PartyB', ['MESSAGESTART', 'Antrag entgegennehmen', 'AnnotationTextTest'], ['Standard', 'Zust pruefen', 'TestOHOH']
    ],
    [
        'PartyC', ['Empty', '', ''], ['Standard', 'FirstTaskFirstBox', 'AnnotationText'], ['Standard', 'FirstTaskFirstBox', 'AnnotationText']
    ]
]
```

This is also part of the file, line 312 onwards.
It generates a BPMN diagram with 3 pools. The first element in the list is the name of the pool.
The subsequent elements in each list represent objects that are placed in the pool.
Each object consists of three parts, its type, text-label and annotation-label. 
All three have to be present, but the annotation-label can be an empty string.

## Scripts

- XMLGenerator
    - very basic function that extracts several important elements from the IOB data (annotated document) and generates an input structure for the bpmn_generator from this
- bpmn_generator
    - parses a given input structure (as explained in the intro) and outputs the corresponding XML
    - was created by reverse-engineering through trial and error (creating diagrams on bpmn.io and looking at their XML)


## Further Development

For experimentation and further development, the `bpmn_generator_experimental.js` script can be used.
It has the same function as the normal script, but works without the rest of the web application and creates a bpmn diagram as output.
The XMLGenerator is not required.

```bash
node bpmn_generator_experimental.js
```

This command will use the predefined input and create a bpmn diagram based on it.


# old documentation

> probably still valid in large parts


#### Process view



##### Code

The code that generates the `bpmn xml` file is part of a web application and provides its functionality in the form of a function to the javascript that is executed by the web application. 

```
.
├── src
│   ├── routes
│   │   ├── process
│   │   │    ├──+page.svelte (actual logic for IOB -> BPMN XML)
│   │   │    ├──AnnotationView.svelte (not relevant for this)
│   │   │    ├──BpmnModeler.svelte (displays bpmn modeler, expects xml input)
│   │   │    ├──generate_bpmn.js (imported by +page.svelte)


```



##### Web Application Javascript

The function `generate_bpmn` expects as input a custom structure that is based on lists. The first level lists define the lanes that will be added to the diagram, and each element in these lists corresponds to a visual element that will be added within that lane. Each of these elements consists of three properties, its name, type and annotation text (if desired).

The web application initially only receives the annotated IOB from the previous view that the user accessed, so the IOB formatted information has to be converted into the input structure that the `generate_bpmn` function expects. The entire logic that determines what elements are placed where and with what symbols and annotations is happening here. 

1. First, we create a list of tuples (entity, class) containing all annotations from the text (function `extract_entities`)

2. We then identify the most frequently occurring entities for the classes `result receivers` and `main actors` and store these as `selected_result_receiver` and `selected_main_actor`. We also extract all entities annotated as `participants`. 

3. Then, for each of these, we initialize an empty list that will be filled with all actions and other elements that should end up in their "lanes" in the bpmn diagram.

4. Finally, we iterate through the list of tuples again, this time processing it while iterating through it. For each tuple we check what its class is and we use a variable called `recent_action_actor` to keep track of what actor was last mentioned in the text.

5. If its class is `result receiver`/`main actor`and the entity is the same as the `actual_results_reciver`/`actual_main_actor`(the most frequent ones) we update the `recent_action_actor`. 

6. On the first encounter of a `main actor` entitiy we add some boilerplate action elements to its lane ("receive request", "check responsibility"). 

7. When we encounter a `participant` we dont set the `recent_action_actor` to the actual participant that we encountered, but to a random one of the participants seen until now.

8. When we encounter a `Handlungsgrundlage` we check if the `recent_action_actor` is set, and if it is, we assign the `Handlungsgrundlagen` entity to its annotation property.

9. When we encounter an `Aktion` we chose a random member of the participants added until now or the main_actor, or results_receiver, and add it to that lane.

10. The other classes (Signalwort, Frist, Bedingung, Dokument, Datenfeld) are currently not involved in the bpmn generation. Their entities are extracted from the list of tuples and stored in lists that are displayed to the user as additional information.

> This generation of the input structure for the bpmn-generator is just a temporary solution until we developed more reasonable rules. The entire input structure will also be refactored at that point.


The Custom Input Structure that we use as intermediary between the IOB text and the bpmn-xml generator serves as a compatibility layer that allows us to change the IOB extraction logic separately from the logic that generates the bpmn xml. It can also be used to manually use the bpmn generator script, because descriptions of diagrams using the Custom Input Structure can be created easily and intuitively by humans.

```
IOB text --> Custom Input Structure --> bpmn xml
text         visual (sort of)           abstract visual                     
```

Example for the input structure
```
let input = [
    [
        'actor_1', ['Standard', 'TaskBox', 'AnnotationText']
    ],
    [
        'actor_2', ['MESSAGESTART', 'Antrag entgegennehmen', 'AnnotationText'], ['Standard', 'Zust pruefen', 'AnnoationText']
    ],
    [
        'actor_3', ['Empty', '', ''], ['Standard', 'TaskBox', 'AnnotationText'], ['Standard', 'TaskBox', 'AnnotationText3']
    ]
]
```

##### BPMN Generator Javascript

> Because we want to build an xml-document step by step, going back and forth and modifying children and parents, we could not use an already available xml-building-library, but instead came up with our own structure that uses a `CustomNode` class to build a tree, which can then be parsed recursively into a single string. Implementing this ourselves keeps the number of dependencies low, the additional code with functions that we dont use low, and allows for a high degree of customizability.

The CustomNode class has 4 attributes:
- tag (xml tag type)
- values (attributes of the tag)
- children (CustomNode List, tags to be nested inside this tag)
- text (content of the xml tag)

The `CustomNode` class only has one method, that is, "toString", which recursively generates a string for the xml element, including its children, tag, values and text.

Starting with a root element and some boiler-plate xml elements, the desired bpmn xml is built by iterating through the input structure described in the previous section. Each "lane" is built after another. Lots of helper functions were created, that perform the required insertions into the xml for the desired visual effects (e.g. adding a label and assigning it to the correct element).

The way that the bpmn xml is structured and correctly formatted was figured out through reverse-engineering, as I did not find any helpful documentation. I started by creating simple bpmn diagrams and then adding more and more elements, always trying to re-model it with the generator script, adding functions where necessary.

The final structure of the CustomNode Tree corresponds to the XML that the generator function returns.

Currently the script and input structure do not support arrows between elements. The input structure and script do support:
- creation of lanes and insertion of elements into them
- two types of icons filled with the tag-text  (type: Standard, MESSAGESTART)
- whitespace insertion in a lane (type: Empty)
- annotation text connected to a single element (3rd field in list)



##### Sources
Besides the bpmn modeler (and the other requirements listed at "Code Requirements") no other sources were used as far as I remember. This was mostly an engineering issue, not a research issue.

- https://github.com/bpmn-io

##### Code Requirements

- the BPMN Generator requires `DOMParser` and `XMLSerializer` from the `xmldom` library (javascript, npm) for prettifying the generated xml string (parse, then serialize again)
- otherwise, when the entire web application is run, check the requirements in the `package.json`


##### Usage

- (disclaimer: this is not thought to be run manually by itself)
- the `generate_bpmn.js` file exports a single function that is the `bpmn_generator` function described in the text above, it expects the structure of nested lists described above as input and returns a single string containing prettified xml
- in case of manual usage the input structure will have to be created manually, an example can be found in a comment in the `generate_bpmn.js` file



- Refer to last README version on the front end branch, with instruction of how to run code (check if it should be extended/updated): [@hil-front-end]
