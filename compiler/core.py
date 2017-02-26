"""
Squiggly compiler module
"""

# given a list of block locations and block IDs, return a list of
# commands to execute
def compile(blocks):
    lines = lineate(blocks)
    commands = simulate(lines)
    return commands


# organize the blocks in lines
def lineate(blocks):
    return []


# simulate the lines to get an explicit list of commands
def simulate(lines):
    return []
