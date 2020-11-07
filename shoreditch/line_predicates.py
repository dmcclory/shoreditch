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

def parse_title_line(line):
    if '(' not in line:
        return [line, {}]

    [title, raw_annotation] = line.split('(')
    title = title.strip()
    raw_annotation = raw_annotation.replace(')', '')

    annotation_pairs = [[f.strip() for f in e.split(':')] for e in raw_annotation.split(',')]
    annotations = dict(annotation_pairs)


    return [title, annotations]
