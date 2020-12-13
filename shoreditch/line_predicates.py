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


def parse_annotation_item(chunk):
    if re.match('^s(\d+)$', chunk):
        match = re.match('^s(\d+)$', chunk)
        return [('type', 'tv_show'), ('season', match.groups()[0])]
    elif re.match('^vol\.(\d+)$', chunk):
        match = re.match('^vol\.(\d+)$', chunk)
        return [('volume', match.groups()[0])]
    else:
        return [list([f.strip() for f in chunk.split(':')])]

def parse_title_line(line):
    if '(' not in line:
        return [line, {}]

    [title, raw_annotation] = line.split('(')
    title = title.strip()
    raw_annotation = raw_annotation.replace(')', '')

    annotation_pairs = []

    for e in raw_annotation.split(','):
        parsed_items = parse_annotation_item(e)
        for pi in parsed_items:
            annotation_pairs.append(pi)

    if len(annotation_pairs[0]) == 1:
        annotation_pairs = [('note', annotation_pairs[0][0])]

    try:
        annotations = dict(annotation_pairs)
    except:
        import pdb; pdb.set_trace()

    if annotations.get('season', ''):
        title = '{} (s{})'.format(title, annotations['season'])

    if annotations.get('volume', ''):
        title = '{} (vol.{})'.format(title, annotations['volume'])


    return [title, annotations]
