# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import os.path
import datetime
import pypandoc
import logging

import taglibro.config
config = taglibro.config.get_config()


class Entry:
    def __init__(self, **kwargs):
        self.path = kwargs.get('path', None)
        self.tags = kwargs.get('tags', [])
        self.date = kwargs.get('date', None)
        self.body = kwargs.get('body', None)
        self.other_headers = kwargs.get('other_headers', {})

    def from_frontend(self, e):
        for key, val in e['header'].items():
            if key == 'date':
                date_fmt = '%d-%m-%Y %H:%M'
                self.date = datetime.datetime.strptime(val, date_fmt)
            elif key == 'tags':
                self.tags = e.tags
            else:
                self.other_headers[key] = val

        self.body = e['body']['txt']

    def push(self):
        if self.path is None:
            raise Exception('no path in Entry')

        if self.date is None or self.tags is [] or self.body == '':
            logging.info('empty header: {}'.format(self.path))
            raise ValueError('Entry is empty.')

        entry_txt = '---\n'
        entry_txt += 'date: {}\n'.format(self.date.strftime('%d-%m-%Y %H:%M'))
        entry_txt += 'tag: {}\n'.format(', '.join(self.tags))
        for key, val in self.other_headers.items():
            entrentry_txt += '{}: {}'.format(key, val)
        entry_txt += '---\n'
        entry_txt += '\n'
        entry_txt += self.body

        with open(self.path, 'w') as f:
            f.write(entry_txt)

    def parse(self):
        if self.path is None:
            raise Exception('no path in Entry')

        if not os.path.exists(self.path):
            logging.info('path does not exist: {}'.format(self.path))
            raise Exception('file does not exist')

        with open(self.path, 'r') as f:
            txt = f.read()
        self.parse_header(txt)
        self.parse_body(txt)

    def parse_header(self, txt=None):
        if txt is None:
            with open(self.path, 'r') as f:
                txt = f.read()
        # if txt.count(header_del) != 2:
            # raise ValueError('missing header or bad formating')

        header_del = '---\n'
        header = txt.split(header_del)[1]
        self.header_txt = header
        header = header.splitlines()

        for line in header:
            sep_i = line.find(':')
            key = line[:sep_i]
            payload = line[sep_i+1:]

            if key == 'date':
                # take away undesired spaces
                date_sep = payload.split(' ')
                date_sep = [s for s in date_sep if s != '']
                date_txt = ' '.join(date_sep)
                if len(date_sep) == 1:

                    date_fmt = '%d-%m-%Y'
                else:
                    date_fmt = '%d-%m-%Y %H:%M'
                # parse datetime
                self.date = datetime.datetime.strptime(date_txt, date_fmt)
            elif key == 'tag':
                tags = payload.split(',')
                tags = [t.strip() for t in tags if t != '']
                self.tags = tags
            else:
                self.other_headers[key] = payload

    def parse_body(self, txt=None):
        if txt is None:
            with open(self.path, 'r') as f:
                txt = f.read()
        # if txt.count(header_del) != 2:
        #     raise ValueError('missing header or bad formating')

        header_del = '---\n'
        body = txt.split(header_del)[-1]
        self.body = body

    def __repr__(self):
        return '<Entry(date={} tag={})>'.format(self.date, self.tags)


def get_entry_list():
    entry_dirs = config['journal_paths']
    entry_paths = []
    for edir in entry_dirs:
        if not os.path.exists(edir):
            raise Exception('entry directory does not exist')
        for root, folders, files in os.walk(edir):
            valid_files = [os.path.join(root, f)
                            for f in files if f[-3:] == '.md']
            entry_paths += valid_files
    entries = [Entry(path=p) for p in entry_paths]
    for e in entries:
        e.parse()

    sorted_entries = sorted(entries, key=lambda x: x.date, reverse=True)
    return sorted_entries
