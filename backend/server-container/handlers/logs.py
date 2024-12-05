import json
import html

def handle_get_logs():
    """ 
        Retrieves logs from files and parses them into the desired structure.
    """

    # todo: make these paths configurable via config
    logs = {}
    logs["server"] = parse_log_file('./shared/logs/server.log')
    logs["trainer"] = parse_log_file('./shared/logs/trainer.log')
    logs["predictor"] = parse_log_file('./shared/logs/predictor.log')

    # from each, remove the last element if its empty
    try:
        for key in logs:
            if logs[key][-1] == "":
                logs[key].pop()

        return logs, 200
    except Exception as e:
        return logs, 500

def parse_log_file(log_file):
    """ 
        Opens the log file at the path provided and parses it.
        Line by line, relevant fields are extracted and user-supplied data is escaped.

        Does not handle stack traces that ended up in the logs very well.
    """
    parsed = []
    logs = ""

    # read the last 500 lines (logfiles only get bigger and bigger)
    with open(log_file, 'r') as file:
        logs = file.readlines()[-500:]

    for line in logs:

        try:

            if line == "":
                continue

            # parse the line
            elements = line.split(" - ")

            # todo: make sure this does not allow for injection

            # todo: sometimes there are stacktraces in here, that mess up the parsing

            message = ""
            for i in range(3, len(elements)):
                message += elements[i]

            parsed.append({
                "timestamp":   html.escape(elements[0].strip()),
                "level":       html.escape(elements[1].strip()),
                "module":      html.escape(elements[2].strip()),
                "message":     html.escape(message.strip())
            })
        except Exception as e:
            continue
        
    return parsed