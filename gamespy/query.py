def parse_message(message):
    tokens = message.split('\\')[1:-1]
    if 'final' not in tokens:
        raise RuntimeError("Message does not terminate, cannot parse.")
    parsed = {}
    if len(tokens) < 2: # No command supplied
        return (parsed, '\\' + '\\'.join(tokens[i:] + '\\'))
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
    list_stack = []
    query = ""
    for key, value in messages:
        if not isinstance(value, list):
            if key != '__cmd__' and key != '__cmd_val__':
                query += '\\' + str(key)
            query += '\\' + str(value)
        else:
            if list_stack and len(value) != len(list_stack[0]):
                interleaved_list = [val for tup in zip(*list_stack) for val in tup]
                query += '\\' + '\\'.join(interleaved_list)
                list_stack = []
            list_stack.append([(key, item) for item in value])
    if list_stack:
        for i in list_stack:
            query += '\\' + '\\'.join(i)
    query += '\\final\\'

    return query
# If stack is empty
