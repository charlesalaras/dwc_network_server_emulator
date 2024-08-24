def parse_message(message):
    tokens = message.split('\\')[1:-1]
    if 'final' not in tokens:
        raise RuntimeError("Message does not terminate, cannot parse.")
    if len(tokens) < 2: # No command supplied
        return (parsed, '\\' + '\\'.join(tokens[i:] + '\\'))
    parsed = {}
    parsed['__cmd__'] = tokens[0]
    parsed['__cmd_val__'] = tokens[1]
    tokens = tokens[2:]
    remaining = ''
    complete = tokens[-1] == 'final'
    if not complete:
        remaining_tokens = tokens[tokens.index('final') + 1:]
        tokens = tokens[:tokens.index('final')]
        remaining = '\\' + '\\'.join(remaining_tokens) + '\\'
    for key, value in zip(*[iter(tokens)]*2):
        if key in parsed.keys():
            if isinstance(parsed[key], list):
                parsed[key] = parsed[key].append(value)
            else:
                parsed[key] = [parsed[key], value]
        else:
            parsed[key] = value
    return (parsed, remaining)

def create_message(messages):
    query = ""
    for key in messages:
        if key != '__cmd__' and key != '__cmd_val__':
            query += '\\' + str(key)
        query += '\\' + str(messages[key])
    query += '\\final\\'

    return query
