import { DOMParser, XMLSerializer } from '@xmldom/xmldom';
import fs from 'fs';
import path from 'path';
// import fs from 'fs';

class CustomNode {
    /**
     * @param {string} tag
     * @param {any} values
     * @param {CustomNode[]} children
     * @param {string} text
     */
    constructor(tag, values, children, text) {
        this.tag = tag;
        this.values = values;
        this.children = children;
        this.text = text;
    }

    toString() {
        let str = "<" + this.tag;

        for (let key in this.values) {
            str += " " + key + "=\"" + this.values[String(key)] + "\"";
        }

        if (this.text != "") {

            // close start tag, add text
            str += ">" + this.text + "\n"

            // possibly add children
            if (this.children.length > 0) {
                for (let i = 0; i < this.children.length; i++) {
                    str += this.children[i].toString();
                }
            }

            // add full closing tag (if either children or text exist)
            str += "</" + this.tag + ">\n";

        } else {
            // just add potential children
            if (this.children.length > 0) {
                // add children
                str += ">"
                for (let i = 0; i < this.children.length; i++) {
                    str += this.children[i].toString();
                }
                // add full closing tag
                str += "</" + this.tag + ">\n";
            } else {
                // no children and no text, just close inital start tag
                str += "/>\n";
            }
        }
        return str;
    }
};

let TASK_HEIGHT = 80;
let TASK_WIDTH = 100;
let LANE_HEIGHT = 250;
let TASK_DISTANCE = 200;
let EVENT_RADIUS = 36;
let LANEHEIGHT = 250;

let lane_coord = 0;
let y_coord = LANE_HEIGHT / 2 - TASK_HEIGHT / 2;

function create_process(processid) {
    let process = new CustomNode("bpmn:process", {
        'id': processid,
    }, [], "")

    return process;
}

function create_bounds(x, y, width, height) {
    let bounds = new CustomNode("dc:Bounds", {
        'x': x,
        'y': y,
        'width': width,
        'height': height
    }, [], "")

    return bounds;
}

// definition of function to add participant
function create_participant(participantid, y, lanewidth, laneheight) {
    let participant = new CustomNode("ns0:BPMNShape", {
        'id': participantid + "_di",
        'isHorizontal': 'true',
        'bpmnElement': participantid
    }, [], "")

    participant.children.push(create_bounds(180, y, lanewidth, laneheight))
    participant.children.push(create_label())

    return participant;
}

function create_waypoint(x, y) {
    let waypoint = new CustomNode("di:waypoint", {
        'x': x,
        'y': y
    }, [], "")

    return waypoint;
}

function create_label() {
    return new CustomNode("ns0:BPMNLabel", {}, [], "")
}

function create_task(activityid, label) {
    let task = new CustomNode("bpmn:task", {
        'id': activityid,
        'name': label
    }, [], "")

    return task;
}


function add_event(root, diagram, processid, eventlabel, x, y, textannotation = "") {
    let rand = Math.floor(Math.random() * 16777215).toString(16);
    let eventid = "event_" + rand;

    let shape = new CustomNode("ns0:BPMNShape", {
        'id': eventid + "_di",
        'bpmnElement': eventid
    }, [], "")

    let bpmnPlane = get_bpmnPlane(root);

    shape.children.push(create_bounds(x, y, EVENT_RADIUS, EVENT_RADIUS))
    let label = create_label()
    label.children.push(create_bounds(x - 25, y + 43, 86, 27))

    bpmnPlane.children.push(shape);

    for (let i = 0; i < root.children.length; i++) {
        if (root.children[i].values.id == processid) {
            // add task to bpmndefinitions
            let task = create_startEvent(eventid, eventlabel);
            let eventdef = create_messageEvent(rand)

            root.children[i].children.push(task);
        }
    }

    add_text_annotation(root, diagram, x - 65, y, textannotation, rand, processid, eventid)

    return eventid;

}

function add_task(root, diagram, processid, activity_label, x, y, textannotation = "") {
    let rand = Math.floor(Math.random() * 16777215).toString(16);
    let activity_id = "activity_" + rand;
    let shape = new CustomNode("ns0:BPMNShape", {
        'id': activity_id + "_di",
        'bpmnElement': activity_id
    }, [], "")

    shape.children.push(create_bounds(x, y, TASK_WIDTH, TASK_HEIGHT))
    shape.children.push(create_label())

    // add task to bpmnplane
    let bpmnPlane = get_bpmnPlane(root);
    bpmnPlane.children.push(shape);

    for (let i = 0; i < root.children.length; i++) {
        if (root.children[i].values.id == processid) {
            // add task to bpmndefinitions
            root.children[i].children.push(
                create_task(
                    activity_id,
                    activity_label));
        }
    }

    add_text_annotation(root, diagram, x, y, textannotation, rand, processid, activity_id)

    return activity_id
}

function create_messageEvent(eventidnumber) {
    return new CustomNode("bpmn:messageEventDefinition", { "id": "MessageEventDefinition_" + eventidnumber }, [], "")
}

function create_startEvent(eventid, label) {
    return new CustomNode("bpmn:startEvent", { "id": eventid, "name": label }, [], "")
}

function add_text_annotation(root, diagram, x, y, textannotation, tasknumber, processid, activityid) {

    let bpmnPlane = get_bpmnPlane(root);

    if (textannotation != "") {
        let annotationid = "textannotation" + tasknumber;

        let shape = new CustomNode("bpmn:textAnnotation", {
            'id': annotationid
        }, [], "")

        let text = new CustomNode("bpmn:text", {}, [], textannotation)
        shape.children.push(text)

        let association = new CustomNode("bpmn:association", {
            'id': "association_" + tasknumber,
            'sourceRef': activityid,
            'targetRef': annotationid
        }, [], "")

        for (let i = 0; i < root.children.length; i++) {
            if (root.children[i].values.id == processid) {

                root.children[i].children.push(shape);
                root.children[i].children.push(association);
            }
        }

        let annotation_shape = new CustomNode("ns0:BPMNShape", {
            'id': annotationid + "_di",
            'bpmnElement': annotationid
        }, [], "")

        annotation_shape.children.push(create_bounds(x + 130, y - 70, 100, 40))
        annotation_shape.children.push(create_label())
        bpmnPlane.children.push(annotation_shape);

        let edge_shape = new CustomNode("ns0:BPMNEdge", {
            'id': "association_" + tasknumber + "_di",
            'bpmnElement': "association_" + tasknumber
        }, [], "")

        edge_shape.children.push(create_waypoint(x + 100, y))
        edge_shape.children.push(create_waypoint(x + 130, y - 50))
        bpmnPlane.children.push(edge_shape);

    }
}

function get_bpmnPlane(root) {
    for (let i = 0; i < root.children.length; i++) {
        if (root.children[i].tag == "ns0:BPMNDiagram") {
            for (let j = 0; j < root.children[i].children.length; j++) {
                if (root.children[i].children[j].tag == "ns0:BPMNPlane") {
                    return root.children[i].children[j];
                }
            }
        }
    }
}

function add_lane(Root, collaboration, diagram, label_arg, y, lanewidth, laneheight) {
    // get random number 
    let rand = Math.floor(Math.random() * 16777215).toString(16);
    let participantid = "participant_" + rand;

    // add participant to bpmnplane
    let bpmnPlane = get_bpmnPlane(Root);

    bpmnPlane.children.push(
        create_participant(
            participantid,
            y,
            lanewidth,
            laneheight));

    rand = Math.floor(Math.random() * 16777215).toString(16);
    let processid = "process_" + rand;

    // add process(processid) to bpmndefinitions
    Root.children.push(
        create_process(
            processid));

    // add participant to collaboration
    let participant = new CustomNode("bpmn:participant", {
        'id': participantid,
        'name': label_arg,      //labelarg
        'processRef': processid   //processid
    }, [], "")

    collaboration.children.push(participant);
    return processid
}

function add_element(root, type, diagram, processid, labeltext, x_coord, y_coord, annotationtext) {
    if (type == 'Standard') {
        add_task(root, diagram, processid, labeltext, x_coord, y_coord, annotationtext)
    } else if (type == 'MESSAGESTART') {
        add_event(root, diagram, processid, labeltext, x_coord, y_coord, annotationtext)
    } else if (type == 'Empty') {
    } else {
    }
}



/////////// END OF SETUP ///////////

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


export default function generate_bpmn(input) {
    let max_length = 0;
    for (let i = 0; i < input.length; i++) {
        let lengthOfLane = input[i].length;
        max_length = Math.max(max_length, lengthOfLane);
    }

    let lanewidth = 600;
    if (max_length > 2) {
        lanewidth = lanewidth + (max_length - 2) * 150;
    }


    let Root = new CustomNode("bpmn:definitions", {
        'xmlns:bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        //BUG: somehow xmlns:xsi is not added to the root node / removed during parse
        'xsi:schemalocation': 'http://www.omg.org/spec/BPMN/20100524/MODEL BPMN20.xsd',
        'id': 'definitions',
        'xmlns:xsi': '',
        'targetNamespace': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    }, [], "")


    let bpmnDiagram = new CustomNode("ns0:BPMNDiagram", {
        'xmlns:ns0': 'http://www.omg.org/spec/BPMN/20100524/DI',
        'id': 'BPMNDiagram_1'
    }, [], "")

    let bpmnPlane = new CustomNode("ns0:BPMNPlane", {
        'id': 'BPMNPlane_1',
        'bpmnElement': 'collaboration_1'
    }, [], "")

    bpmnDiagram.children.push(bpmnPlane)

    let collaboration = new CustomNode("bpmn:collaboration", {
        'id': 'collaboration_1',
    }, [], "")

    Root.children.push(bpmnDiagram);
    Root.children.push(collaboration);


    input.forEach(laneInfo => {
        let x_coord = 290;
        let processid = add_lane(Root, collaboration, bpmnDiagram, laneInfo[0], lane_coord, lanewidth, LANE_HEIGHT)
        let isFirstIteration = true;
        laneInfo.forEach(task => {

            if (isFirstIteration) {
                // skip first element as it contains lane information
                isFirstIteration = false;
            } else {
                // otherwise add the task
                add_element(Root, task[0], bpmnDiagram, processid, task[1], x_coord, y_coord, task[2])
                x_coord += TASK_DISTANCE
            }
        });
        y_coord += LANE_HEIGHT
        lane_coord += LANE_HEIGHT
    });

    /////////// END OF CODE ///////////
    let xmlString = Root.toString();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlString, "text/xml");
    const serializer = new XMLSerializer();
    const prettyXml = serializer.serializeToString(xmlDoc);


    return prettyXml;
}


// compare output of do_it with bpmn file comp_bpmn.xml

// read the content of the comp file

// const comp_bpmn = fs.readFileSync('comp_output.bpmn', 'utf8');

// if (do_it(input) == comp_bpmn) {
//    console.log("Test passed")
//}

let __dirname = path.resolve(path.dirname(''));
const output = generate_bpmn(input);
const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const filename = path.join(__dirname, `diagram_${timestamp}.bpmn`);

fs.writeFileSync(filename, output, 'utf8');
console.log(`Output written to ${filename}`);