"""
Squiggly compiler module
"""

keywords = {
    'for': 'FOR',
    'forward': 'FWD',
    'turn': 'TRN',
    'chocolate': 'CHC',
    'eat': 'EAT',
    'banana': 'BAN'
}
id_to_keyword = {
    'RBG': keywords['for'],
    'BRB': keywords['forward'],
    'RGR': keywords['turn'],
    'BRG': keywords['chocolate'],
    'BGR': keywords['eat'],
    'RGB': keywords['banana']
}
default_values = {}
default_values[keywords['chocolate']] = 4
default_values[keywords['banana']] = 10
default_values[keywords['forward']] = 1
default_values[keywords['turn']] = 90
default_values[keywords['eat']] = 1


# given a list of block locations and block IDs, return a list of
# commands to execute
def compile(blocks):
    lines = lineate(blocks)
    ast = parse(lines)
    commands = simulate(ast)
    return commands


# organize the blocks in lines
def lineate(blocks):
    return []


# parse lines into an AST
def parse(lines):
    return {
        'type': 'list',
        'info': {
            'body': map(parse_line, lines)
        }
    }


# parse a single line
def parse_line(line):
    ast = {}
    remaining_tokens = []
    if parse_for(line, ast, remaining_tokens):
        return ast
    elif parse_list(line, ast, remaining_tokens):
        return ast
    else:
        return {}


def parse_for(tokens, ast, remaining):
    if len(tokens) < 3:
        return False

    t = tokens[:]
    if t.pop(0) == keywords['for']:
        var_ast = {}
        remaining_tokens = []
        if parse_var(t, var_ast, remaining_tokens):
            t = remaining_tokens
            list_ast = {}
            last_tokens = []
            if parse_list(remaining_tokens, list_ast, last_tokens):
                if len(last_tokens) == 0:
                    ast['type'] = 'for'
                    ast['info'] = {
                        'variable': var_ast,
                        'body': list_ast
                    }
                    return True
    return False


def parse_var(tokens, ast, remaining):
    if len(tokens) < 1:
        return False

    t = tokens[:]
    token = t.pop(0)
    if token == keywords['chocolate'] or token == keywords['banana']:
        ast['type'] = 'var'
        ast['info'] = {
            'name': token,
            'value': default_values[token]
        }
        for leftover in t:
            remaining.append(leftover)
        return True
    return False


def parse_list(tokens, ast, remaining):
    if len(tokens) < 1:
        return False

    ast['type'] = 'list'
    ast['info'] = {
        'body': []
    }
    t = tokens[:]
    last_ast = {}
    last_remaining = []
    while parse_statement(t, last_ast, last_remaining):
        ast['info']['body'].append(last_ast)
        last_ast = {}
        t = last_remaining
        last_remaining = []

    if len(ast['info']['body']) > 0:
        for leftover in last_remaining:
            remaining.append(leftover)
        return True
    else:
        return False


def parse_statement(tokens, ast, remaining):
    if len(tokens) < 1:
        return False

    t = tokens[:]
    last_remaining = []
    if parse_forward(t, ast, last_remaining):
        for leftover in last_remaining:
            remaining.append(leftover)
        return True
    elif parse_turn(t, ast, last_remaining):
        for leftover in last_remaining:
            remaining.append(leftover)
        return True
    elif parse_eat(t, ast, last_remaining):
        for leftover in last_remaining:
            remaining.append(leftover)
        return True
    else:
        return False


def parse_forward(tokens, ast, remaining):
    if len(tokens) < 1:
        return False

    t = tokens[:]
    token = t.pop(0)
    if token == keywords['forward']:
        ast['type'] = 'function'
        ast['info'] = {
            'name': 'forward',
            'arguments': [default_values[keywords['forward']]]
        }
        for leftover in t:
            remaining.append(leftover)
        return True
    else:
        return False


def parse_turn(tokens, ast, remaining):
    if len(tokens) < 1:
        return False

    t = tokens[:]
    token = t.pop(0)
    if token == keywords['turn']:
        ast['type'] = 'function'
        ast['info'] = {
            'name': 'turn',
            'arguments': [default_values[keywords['turn']]]
        }
        for leftover in t:
            remaining.append(leftover)
        return True
    else:
        return False


def parse_eat(tokens, ast, remaining):
    if len(tokens) < 2:
        return False

    t = tokens[:]
    token = t.pop(0)
    if token == keywords['eat']:
        var_ast = {}
        var_remaining = []
        if parse_var(t, var_ast, var_remaining):
            ast['type'] = 'function'
            ast['info'] = {
                'name': 'eat',
                'arguments': [
                    var_ast,
                    default_values[keywords['eat']]
                ]
            }
            for leftover in var_remaining:
                remaining.append(leftover)
            return True
    return False


# simulate the lines to get an explicit list of commands
def simulate(ast):
    commands = []
    state = {}
    simulate_helper(ast, state, commands)
    return commands


def simulate_helper(ast, state, out):
    if ast['type'] == 'function':
        if ast['info']['name'] == 'forward':
            amount = ast['info']['arguments'][0]
            out.append((keywords['forward'], amount))
        elif ast['info']['name'] == 'turn':
            amount = ast['info']['arguments'][0]
            out.append((keywords['turn'], amount))
        elif ast['info']['name'] == 'eat':
            var = ast['info']['arguments'][0]
            var_name = var['info']['name']
            amount = ast['info']['arguments'][1]
            if 'variables' in state:
                state['variables'][var_name] -= amount
    elif ast['type'] == 'list':
        for sub_ast in ast['info']['body']:
            simulate_helper(sub_ast, state, out)
    elif ast['type'] == 'for':
        var_ast = ast['info']['variable']
        var_name = var_ast['info']['name']
        if 'variables' not in state:
            state['variables'] = {}
        state['variables'][var_name] = var_ast['info']['value']
        body_ast = ast['info']['body']
        while state['variables'][var_name] > 0:
            simulate_helper(body_ast, state, out)
