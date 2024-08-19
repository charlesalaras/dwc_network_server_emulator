def parse_message(message):
    tokens = message.split('\\')[1:-1]
    if "final" not in tokens:
        raise RuntimeError("Message does not terminate, cannot parse.")
    if len(tokens) < 2: # No command supplied
        return (parsed, '\\' + '\\'.join(tokens[i:] + '\\'))
    parsed = {}
    parsed['__cmd__'] = tokens[0]
    parsed['__cmd_val__'] = tokens[1]
    tokens = tokens[2:]
    for i in range(0, len(tokens)):
        if tokens[i] == 'final':
            i += 1
            break
        *_, last = parsed.items()
        # FIXME: Have to account for multiple same keys
        if last[1] is None or isinstance(last[1], list): # Incomplete parse from earlier
            if isinstance(last[1], list):
                parsed[last[0]].append(tokens[i])
            else:
                parsed[last[0]] = tokens[i]
        else: # Last parse was complete, just insert
            if tokens[i] not in parsed:
                parsed[tokens[i]] = None
    if i < len(tokens):
        return (parsed, '\\' + '\\'.join(tokens[i:]) + '\\')
    return (parsed, '');

def create_message(messages):
    query = ""
    for key in messages:
        if key != '__cmd__' and key != '__cmd_val__':
            query += '\\' + str(key)
        query += '\\' + str(messages[key])
    query += '\\final\\'

    return query
