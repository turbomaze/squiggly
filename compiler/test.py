import core


def test_parser():
    # test 1: parse forwards
    tokens, ast, remaining = ['FWD'], {}, []
    print 'TESTING PARSE FORWARD'
    print core.parse_forward(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 2: parse turn
    tokens, ast, remaining = ['TRN'], {}, []
    print 'TESTING PARSE TURN'
    print core.parse_turn(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 3: parse turn forward
    tokens, ast, remaining = ['TRN', 'FWD'], {}, []
    print 'TESTING PARSE TURN'
    print core.parse_turn(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 4: parse var
    tokens, ast, remaining = ['CHC'], {}, []
    print 'TESTING PARSE CHOCOLATE'
    print core.parse_var(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 5: parse var
    tokens, ast, remaining = ['CHC'], {}, []
    print 'TESTING PARSE CHOCOLATE'
    print core.parse_var(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 6: parse var
    tokens, ast, remaining = ['EAT', 'CHC'], {}, []
    print 'TESTING PARSE EAT'
    print core.parse_eat(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 7: parse list
    tokens, ast, remaining = ['FWD', 'FWD', 'TRN'], {}, []
    print 'TESTING PARSE LIST'
    print core.parse_list(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 8: parse for
    tokens, ast, remaining = ['FOR', 'CHC', 'FWD'], {}, []
    print 'TESTING PARSE FOR LOOP'
    print core.parse_for(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 8: parse for with eat
    tokens, ast, remaining = [
        'FOR', 'CHC', 'FWD', 'EAT', 'CHC'
    ], {}, []
    print 'TESTING PARSE FOR LOOP WITH EAT'
    print core.parse_for(tokens, ast, remaining)
    print tokens, ast, remaining
    print

    # test 8: parse line for list
    tokens = ['FWD', 'FWD', 'TRN']
    print 'TESTING PARSE LINE WITH LIST'
    ast = core.parse_line(tokens)
    print ast
    print

    # test 9: parse line for for loops
    tokens = ['FOR', 'BAN', 'FWD']
    print 'TESTING PARSE LINE WITH FOR LOOP'
    ast = core.parse_line(tokens)
    print ast
    print

def test_compiler():
    # test 1: compile simple commands
    lines = [['FWD']]
    print 'TESTING COMPILE FORWARD'
    commands = core.simulate(core.parse(lines))
    print commands
    print

    # test 2: compile multiple simple commands
    lines = [['FWD', 'FWD', 'TRN']]
    print 'TESTING COMPILE FORWARD FORWARD TURN'
    commands = core.simulate(core.parse(lines))
    print commands
    print

    # test 3: compile multiple lines
    lines = [['FWD', 'FWD'], ['TRN']]
    print 'TESTING COMPILE FORWARD FORWARD NEWLINE TURN'
    commands = core.simulate(core.parse(lines))
    print commands
    print

    # test 4: compile for loop
    lines = [['FOR', 'CHC', 'FWD', 'TRN', 'EAT', 'CHC']]
    print 'TESTING COMPILE FOR LOOP'
    commands = core.simulate(core.parse(lines))
    print commands
    print

    # test 5: compile for loop and more
    lines = [['FOR', 'CHC', 'FWD', 'TRN', 'EAT', 'CHC'], ['TRN']]
    print 'TESTING COMPILE FOR LOOP AND MORE'
    commands = core.simulate(core.parse(lines))
    print commands
    print

    # test 6: compile a lot of commands
    lines = [
        [
            'FOR', 'CHC',
            'FWD', 'FWD', 'FWD', 'FWD', 'FWD',
            'EAT', 'CHC'
        ]
    ]
    print 'TESTING COMPILE FOR LOOP AND MORE'
    commands = core.simulate(core.parse(lines))
    print commands
    print

if __name__ == '__main__':
    # test_parser()

    test_compiler()
