import re

def blank(line):
    return line == ''

def dateline(line):
    return re.match('^\d+\/\d+', line)
