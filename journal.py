# -*- coding: utf-8 -*-
import os
import os.path
import datetime
import pypandoc
import functools
import warnings

if __name__ == '__main__':
    import webbrowser
    import argparse
    import tempfile
    import sys

    # Support Python 2 and 3 input
    # Default to Python 3's input()
    get_input = input

    # If this is Python 2, use raw_input()
    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input    

    TEMP_DIR = tempfile.gettempdir()

# def to_unicode_or_bust(obj, encoding='utf-8'):
#     if isinstance(obj, basestring):
#         if not isinstance(obj, unicode):
#             obj = unicode(obj, encoding)
#     return obj

JOURNAL_PATH = u'/home/chiroptera/Dropbox/journal'
DROPBOX_IGNORE_CONFLICTED_COPIES = True
BEFORE_BODY_TEMPLATE = u'/home/chiroptera/workspace/journal_app/before_body_code.html'
AFTER_BODY_TEMPLATE = u'/home/chiroptera/workspace/journal_app/after_body_code.html'

ENTRY_SEPARATOR_IMG = u'/home/chiroptera/workspace/journal_app/rsc/entry_separator.png'
ENTRY_SEPARATOR_MD = u'\n* * *\n'
HLINE_HTML = u'<hr />'

class Entry:
    """Object to hold metadata of each journal entry."""
    def __init__(self, path, date=None, tag=None, location=None, time=None,
                 line_start=None, line_end=None):
        self.metadata = dict()
        meta = self.metadata
        self.path = path
        self.tag = tag
        self.date = date
        self.time = time
        self.location = location
        self.line_start = line_start
        self.line_end = line_end

    def parse_field(self, field, value):
        if field in ('tag','tags'):
            if isinstance(value, list):
                self.tag = value
            else:
                raise TypeError('Value of tag must be a list of strings.')
        elif field == 'date':
            try:
                self.date = datetime.datetime.strptime(value[0], '%d-%m-%Y').date()
            except ValueError:
                print('Wrong date formating in file: {}'.format(self.path))
        elif field == 'time':
            try:
                self.time = datetime.datetime.strptime(value[0], '%H:%M').time()
            except ValueError:
                print('Wrong time formating in file: {}'.format(self.path))            
        elif field == 'location':
            if isinstance(value, list):
                self.location = value
            else:
                raise TypeError('Value of location must be a list of strings.')
        else:
            print('Skipping metafield with name: {}'.format(field))
            # raise warnings.warn('Skipping metafield with name: {}'.format(field), DeprecationWarning)

    def get_valid_metadata(self):
        out_dict = dict()
        if self.date is not None:
            out_dict['date'] =  u'{}-{}-{}'.format(self.date.day, self.date.month, self.date.year)
        if self.time is not None:
            out_dict['time'] =  u'{}:{}'.format(self.time.hour, self.time.minute)
        if self.location is not None:
            out_dict['location'] =  u', '.join(self.location)
        if self.tag is not None:
            out_dict['tag'] =  u', '.join(self.tag)

        return out_dict
 
def parse_entries(file_path):
    # read file
    f = open(file_path, 'r')
    lines = f.readlines()
    if len(lines) == 0:
        return []
    ed_list = list()

    # parse entries - reads only metadata
    metadata = False
    just_started = True
    for lnum, line in enumerate(lines):
        # detect start of metadata
        if not metadata and '---' in line:
            if not just_started:
                ed_list[-1].line_end = lnum - 1
            else:
                just_started = False

            metadata = not metadata
            ed_list.append(Entry(file_path))

        # detect end of metadata
        elif metadata and '---' in line:
            metadata = not metadata
            ed_list[-1].line_start = lnum + 1

        # metadata line
        elif metadata:
            metafield, value = line.split(':', 1) # max of 1 split - important for time
            value = value.split(',')
            value = [v.strip() for v in value]

            ed_list[-1].parse_field(metafield, value)

    ed_list[-1].line_end = lnum
    try:
        ed_list[-1].line_end = lnum
    except Exception:
        print('hello')
    return ed_list

def compile_to_html(text, output_path):
    f1 = open(BEFORE_BODY_TEMPLATE, 'r')
    f2 = open(AFTER_BODY_TEMPLATE, 'r')

    output = f1.read() # header with style
    # output += pypandoc.convert(text, 'html', format='md') # text body
    output += text
    output += f2.read() # closing statements

    fo = open(output_path, 'w')
    output = output.encode('utf-8')
    fo.write(output)


def get_entries(entry_list, start_date=None, end_date=None,
                tags_include=None, tags_exclude=None):

    working_list = entry_list
    if start_date is not None:
        working_list = filter(lambda x: x.date >= start_date, working_list)
        working_list = [e for e in working_list]
    if end_date is not None:
        working_list = filter(lambda x: x.date <= end_date, working_list)
        working_list = [e for e in working_list]

    if tags_include is not None:
        def check_common_tag_inclde(entry):
            # return true if there is a common tag
            for e in entry.tag:
                if e in tags_include:
                    return True
            return False
        working_list = filter(check_common_tag_inclde, working_list)
        working_list = [e for e in working_list]

    if tags_exclude is not None:
        def check_common_tag_exclude(entry):
            # return false if there is a common tag
            for e in entry.tag:
                if e in tags_exclude:
                    return False
            return True
        working_list = filter(check_common_tag_exclude, working_list)    
        working_list = [e for e in working_list]

    return working_list

def html_from_entries(entry_list, output_path):
    # sort entries
    entry_list.sort(key=lambda x: x.date)

    # get unique paths
    path_list = list()
    for e in entry_list:
        if e.path not in path_list:
            path_list.append(e.path)

    # get text from all entries including metadata
    text_list = list()
    for p in path_list:
        f = open(p, 'r')
        txt = f.read()
        f.close()

        txt = txt.split('---\n')[1:]
        text_list.extend(txt)

    end_of_entry = u'<img src="{}" style="horizontal-align:middle" />'.format(ENTRY_SEPARATOR_IMG)

    # assemble all texts in html body
    output_txt = u''
    for i in range(0, len(text_list), 2):
        entry_meta = text_list[i]
        entry_meta = entry_meta.splitlines()
        entry_meta = map(lambda x: '<p>{}</p>'.format(x),entry_meta)
        entry_meta = functools.reduce(lambda x,y: x+y, entry_meta)
        # entry_meta = to_unicode_or_bust(entry_meta)

        entry_txt = text_list[i+1]
        # entry_txt = to_unicode_or_bust(entry_txt)
        entry_txt = pypandoc.convert(entry_txt, 'html', format='md')

        output_txt = u'{}\n{}\n{}\n{}\n{}\n'.format(output_txt,
                                                       entry_meta, HLINE_HTML,
                                                       entry_txt, end_of_entry)

    compile_to_html(output_txt, output_path)

def html_from_entries2(entry_list, output_path):
    # sort entries
    entry_list.sort(key=lambda x: x.date)

    # get unique paths
    path_list = list()
    for e in entry_list:
        if e.path not in path_list:
            path_list.append(e.path)

    # get text of each entry
    entry_texts = dict()
    for e in entry_list:
        with open(e.path, 'r') as f:
            alllines = f.readlines()
            entry_texts[e] = ''.join(alllines[e.line_start:e.line_end+1])

    end_of_entry = u'<img src="{}" style="horizontal-align:middle" />'.format(ENTRY_SEPARATOR_IMG)

    # assemble all texts in html body
    output_txt = u''
    for e in entry_list:
        # write metadata
        metadata = e.get_valid_metadata()
        metatext = u''
        for metafield, value in metadata.items():
            metatext = '{}<p>{}: {}</p>\n'.format(metatext, metafield, value)
        output_txt = u'{}\n{}\n{}'.format(output_txt,
                                         metatext,
                                         HLINE_HTML)
        # write entry text
        html_text = pypandoc.convert(entry_texts[e], 'html', format='md')
        output_txt = u'{}{}\n{}\n'.format(output_txt, html_text, end_of_entry)

    compile_to_html(output_txt, output_path)

def get_week_entries(entry_list, output_path,
                     tags_include=None, tags_exclude=None):
    weekly_list = filter(lambda x: 'vecka' in x.tag, entry_list)
    entry = None
    for entry in weekly_list:
        pass
    weekly_last_date = entry.date

    week_list = get_entries(entry_list,
                            start_date=weekly_last_date,
                            tags_include=tags_include,
                            tags_exclude=tags_exclude)
    html_from_entries2(week_list, output_path)

def get_month_entries(entry_list, output_path):
    monthly_list = filter(lambda x: 'månad' in x.tag, entry_list)

    if len(monthly_list) is not 0:
        entry = None
        for entry in monthly_list:
            pass        
        monthly_last_date = entry.date
    else:
        monthly_last_date = entry_list[0].date

    monthly_list = get_entries(entry_list, start_date=monthly_last_date)
    html_from_entries2(monthly_list, output_path)    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Journal access.')
    parser.add_argument('-w', '--weekly', action='store_true',
                        help='Compile all entries from the last weekly entry.')
    parser.add_argument('-m', '--monthly', action='store_true',
                        help='Compile all "vecka" entries from the last monthly entry.')
    parser.add_argument('-et', '--exclude-tag', nargs='+', type=str, default=None,
                        help='Specify which tags to exclude.')
    parser.add_argument('-it', '--include-tag', nargs='+', type=str, default=None,
                        help='Specify which tags to include.')

    args = parser.parse_args()

    # list of absolute paths of all entries
    path_list = list()
    for root, dirs, files in os.walk(JOURNAL_PATH):
        for name in files:
            path_list.append(os.path.join(root, name))

    # remove files not of .md or .markdown extension
    def is_correct_type(path):
        if '.md' in path:
            return True
        if '.markdown' in path:
            return True
        return False

    path_list = filter(is_correct_type, path_list)
    path_list = [p for p in path_list]

    # remove conflicted copies form Dropbox
    def not_conflicted_copy(string):
        if 'conflicted copy' in string:
            return False
        return True
    
    if DROPBOX_IGNORE_CONFLICTED_COPIES:
        path_list = filter(not_conflicted_copy, path_list)
        path_list = [p for p in path_list]

    # parse all entries from all files
    entry_list = list()
    for path in path_list:
        entry_list.extend(parse_entries(path))

    # sort all entries by date
    entry_list.sort(key=lambda x: x.date)

    if args.weekly:
        path = os.path.join(TEMP_DIR, 'weekly_entry.html')
        get_week_entries(entry_list, path,
                         tags_include=args.include_tag,
                         tags_exclude=args.exclude_tag)

        ans = get_input('Open in browser? (y/n)')
        print ans, type(ans)
        if ans in ['y','Y']:
            webbrowser.open(path, new=0, autoraise=True)

    if args.monthly:
        path = os.path.join(TEMP_DIR, 'monthly_entry.html')
        get_month_entries(entry_list, path)

        ans = get_input('Open in browser? (y/n)')
        if ans in ['y','Y']:
            webbrowser.open(path, new=0, autoraise=True)