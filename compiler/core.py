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

# given a list of block locations and block IDs, return a list of
# commands to execute
def compile(blocks):
    lines = lineate(blocks)
    commands = simulate(lines)
    return commands


# organize the blocks in lines
def lineate(blocks):
    return blocks


# simulate the lines to get an explicit list of commands
def simulate(lines):
    return lines
