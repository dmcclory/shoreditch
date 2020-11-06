import re

def blank(line):
    return line == ''

def dateline(line):
    return re.match('^\d+\/\d+', line)

def yearline(line):
    return re.match('^\s*---\s*(\d+)\s*---', line)

def extract_year(line):
    match = yearline(line)
    return match.groups()[0]
