from lxml import etree
import random


// this is the bpmn-generator, which was initially written in Python and then manually translated to JavaScript
// it can now be found here: frontend/src/lib

random.seed(10)
TASK_HEIGHT = 80
TASK_WIDTH = 100
LANE_HEIGHT = 250
TASK_DISTANCE = 200
EVENT_RADIUS = 36
LANEHEIGHT = 250
lanewidth = 600 # will be changed dynamically

def create_definitions():
    etree.register_namespace('bpmn', 'http://www.omg.org/spec/BPMN/20100524/MODEL')
    etree.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    etree.register_namespace('dc','http://www.omg.org/spec/DD/20100524/DC')
    etree.register_namespace('di','http://www.omg.org/spec/DD/20100524/DI')
    definitions = etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}definitions', attrib={
        '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 'http://www.omg.org/spec/BPMN/20100524/MODEL BPMN20.xsd',
        'id': 'definitions',
        'targetNamespace': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    })

    return definitions

def create_collaboration():
    return etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}collaboration', attrib={'id': 'collaboration_1'}) 

def create_bpmndi_diagram():
    bpmndi_diagram = etree.Element('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNDiagram', attrib={'id': 'BPMNDiagram_1'})
    bpmn_plane = etree.Element('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNPlane', attrib={'id': 'BPMNPlane_1', 'bpmnElement': 'collaboration_1'})
    bpmndi_diagram.append(bpmn_plane)
    return bpmndi_diagram

def get_bpmnplane(diagram):
    return diagram.find('.//{http://www.omg.org/spec/BPMN/20100524/DI}BPMNPlane')

def create_process(processid):
    return etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}process', attrib={'id': processid})

def create_label():
    return etree.Element('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNLabel')

def create_participant(participantid, y, lanewidth, laneheight):
    participant = etree.Element('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNShape', attrib={
        'id': str(participantid) + "_di", 
        'bpmnElement': participantid,
        'isHorizontal': 'true'
    })
    
    bounds = etree.Element('{http://www.omg.org/spec/DD/20100524/DC}Bounds', attrib={'x': '180', 'y': str(y), 'width': str(lanewidth), 'height': str(laneheight)})
    participant.append(bounds)
    participant.append(create_label())
    return participant

def get_by_id(root, id):
    return root.xpath(f"//*[@id='{id}']")

def addLane(root, collaboration, diagram, label_arg, y, lanewidth, laneheight):
    random_number = random.randint(1, 1000)
    participantid = 'participant_'+str(random_number)

    participant = create_participant(participantid, y, lanewidth, laneheight)
    bpmn_plane_reference = get_bpmnplane(diagram)
    bpmn_plane_reference.append(participant)

    processid = 'process_'+str(random.randint(1, 1000))

    root.append(create_process(processid))

    # also add participant to collaboration
    participant = etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}participant', attrib={'id': participantid, 'name': label_arg, 'processRef':processid})
    collaboration.append(participant)
    return processid, participantid

def create_task(activityid, label):
    return etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}task', attrib={'id': activityid, 'name': label})

def create_waypoint(x, y):
    return etree.Element('{http://www.omg.org/spec/DD/20100524/DI}waypoint', attrib={'x': str(x), 'y': str(y)})

def create_bounds(x, y, width, height):
    return etree.Element('{http://www.omg.org/spec/DD/20100524/DC}Bounds', attrib={'x': str(x), 'y': str(y), 'width': str(width), 'height': str(height)})

def add_text_annotation(root, diagram, x, y, textannotation, tasknumber, processid, activityid):
    # now add the textannotation (or dont, if empty)
    bpmn_plane_reference = get_bpmnplane(diagram)
    if textannotation != "":
        textannotationid = 'textannotation_' + str(tasknumber)
        # add annotation to process
        process_reference = root.xpath(f"//*[@id='{processid}']")
        print("adding task to processid: ", processid)
        if process_reference:
            task = etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}textAnnotation', attrib={'id': textannotationid})
            text = etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}text')
            # this should be
            text.text = textannotation

            task.append(text)
            process_reference[0].append(task)

            association = etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}association', attrib={'id': 'Association_' + str(tasknumber), 'sourceRef': activityid, 'targetRef': textannotationid})
            process_reference[0].append(association)

        # add shape of text to plane
        annotation_shape = etree.Element('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNShape', attrib={'id': 'textannotation_' + str(tasknumber) + "_di", 'bpmnElement':'textannotation_' + str(tasknumber)})
        annotation_shape.append(create_bounds(x+130, y-70, 100, 40))
        annotation_shape.append(create_label())
        bpmn_plane_reference.append(annotation_shape)

        # add edge to plane
        edge_shape = etree.Element('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNEdge', attrib={'id': 'Association_' + str(tasknumber) + "_di", 'bpmnElement':'Association_' + str(tasknumber)})

        # add start and end points to edge
        edge_shape.append(create_waypoint(x+100, y))
        edge_shape.append(create_waypoint(x+100+30, y-50))
        bpmn_plane_reference.append(edge_shape)

def add_task(root, diagram, processid, activity_label, x, y, textannotation=""):
    bpmn_plane_reference = get_bpmnplane(diagram)
    tasknumber = random.randint(1, 1000)
    activityid = 'activity_' + str(tasknumber)

    activitybox = etree.Element('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNShape', attrib={'id': activityid + "_di", 'bpmnElement': activityid})
    activitybox.append(create_bounds(x, y, TASK_WIDTH, TASK_HEIGHT))

    activitybox.append(create_label())
    bpmn_plane_reference.append(activitybox)

    # connect activitybox to process
    process_reference = get_by_id(root, processid)
    print("adding task to processid: ", processid)
    if process_reference:
        process_reference[0].append(create_task(activityid, activity_label))
    else:
        print("Process not found.")

    add_text_annotation(root, diagram, x, y, textannotation, tasknumber, processid, activityid)

    return activityid

def create_startevent_abstract(eventid, label):
    return etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}startEvent', attrib={'id': eventid, 'name': label})

def create_messageEventDefinition_abstract(eventidnumber):
    return etree.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}messageEventDefinition', attrib={'id': 'MessageEventDefinition_' + str(eventidnumber)})

def prettify(element):
    return etree.tostring(element, pretty_print=True, encoding='unicode')

def add_event(root, diagram, processid, eventlabel, x, y, textannotation=""):
    bpmn_plane_reference = get_bpmnplane(diagram)
    random_number = random.randint(1, 1000)
    eventid = 'event_' + str(random_number)

    # create event entry in plane, then add bounds
    eventShape = etree.Element('{http://www.omg.org/spec/BPMN/20100524/DI}BPMNShape', attrib={'id': eventid + "_di", 'bpmnElement':eventid})
    eventShape.append(create_bounds(x, y, EVENT_RADIUS, EVENT_RADIUS))

    # add label with its own bounds
    label = create_label()
    label.append(create_bounds(x-25, y+43, 86, 27)) # center label below event
    eventShape.append(label)
    bpmn_plane_reference.append(eventShape)

    # append to process (connect diagram and information, is necessary)
    process_reference = root.xpath(f"//*[@id='{processid}']")
    print("adding event to processid: ", processid)
    if process_reference:
        task = create_startevent_abstract(eventid, eventlabel)
        
        eventDef = create_messageEventDefinition_abstract(random_number)
        task.append(eventDef)
        
        process_reference[0].append(task)
    else:
        print("Process not found.")

    # -65 due to smaller width of event elements compared to tasks
    add_text_annotation(root, diagram, x-65, y, textannotation, random_number, processid, eventid)
    
    return eventid

def add_element(root, type, diagram, processid, labeltext, x_coord, y_coord, annotationtext):
    if type == 'MESSAGESTART':
        add_event(root, diagram, processid, labeltext, x_coord, y_coord, annotationtext)
    elif type == "Empty":
        pass
    elif type == "Standard":
        add_task(root, diagram, processid, labeltext, x_coord, y_coord, annotationtext)
    else:
        print("Error: Encountered unsupported type")

def generate_bpmn(input):
    root = create_definitions()
    diagram = create_bpmndi_diagram()
    root.append(diagram)
    collaboration = create_collaboration()
    root.append(collaboration)

    ## HERE WE ARE RIGHT NOW

    ############ PROCESS INPUT ############
    lane_coord = 0 # starting coords
    y_coord = LANE_HEIGHT/2 - TASK_HEIGHT/2 # center elements vertically in lane

    # find max number of elements in single lane
    max_length = 0
    for x in input:
        max_length = max(len(x), max_length)

    lanewidth = 600
    if max_length > 2:
        # scale lane width with maximum number of tasks in a lane
        lanewidth = lanewidth + (max_length - 2) * 150

    for x in input:
        x_coord = 290 # left padding to lane start
        # add participant to diagram
        processid, _ = addLane(root, collaboration, diagram, x[0], lane_coord, lanewidth, LANE_HEIGHT)
        for task in x[1:]:
            add_element(root, task[0], diagram, processid, task[1], x_coord, y_coord, task[2])
            x_coord += TASK_DISTANCE
        y_coord += LANE_HEIGHT
        lane_coord += LANE_HEIGHT

    return root


if __name__ == '__main__':
    # this is a sample input which creates 3 lanes
    # the first lane has one task, the second lane has one event and a task
    # the third lane is empty
    # MESSAGESTART is currently the only available special symbol
    input = [
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

    result = generate_bpmn(input)

    with open("output.bpmn", 'w') as f:
        f.write(prettify(result))

    with open("comp_output.bpmn", "r") as f:
        reference = f.read()

    if reference != prettify(result):
        print("ERROR")
    else:
        print("SUCCESS")