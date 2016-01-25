import os
from os.path import join
#import cPickle
import datetime
import pypandoc

def to_unicode_or_bust(obj, encoding='utf-8'):
	if isinstance(obj, basestring):
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj

JOURNAL_PATH = u'/home/chiroptera/Dropbox/journal'
DROPBOX_IGNORE_CONFLICTED_COPIES = True
BEFORE_BODY_TEMPLATE = u'/home/chiroptera/workspace/journal_app/before_body_code.html'
AFTER_BODY_TEMPLATE = u'/home/chiroptera/workspace/journal_app/after_body_code.html'

ENTRY_SEPARATOR_IMG = u'/home/chiroptera/workspace/journal_app/rsc/entry_separator.png'
ENTRY_SEPARATOR_MD = u'\n* * *\n'
HLINE_HTML = u'<hr />'

class Entry:
	"""Object to hold metadata of each journal entry."""
	def __init__(self, path, date, tags, line_start=None, line_end=None):
		self.path = path
		self.tags = tags
		self.date = date
		self.line_start = line_start
		self.line_end = line_end
 
def parse_entries(file_path):
	# read file
	f = open(file_path, 'r')
	lines = f.readlines()
	ed_list = list()

	# parse entries - reads only metadata
	metadata = False
	for line in lines:
		if '---' in line:
			metadata = not metadata
			if metadata:
				ed_list.append(dict())

		elif metadata:
			# some entries have a space between ':' and the date string
			if 'date: ' in line:
				date = datetime.datetime.strptime(line, "date: %d-%m-%Y\n").date()
				ed_list[-1]['date'] = date			
			elif 'date:' in line:
				date = datetime.datetime.strptime(line, "date:%d-%m-%Y\n").date()
				ed_list[-1]['date'] = date
			elif 'tags:' in line:
				tags = line.strip('tag:')
				tags = tags.strip('\n')
				tags = tags.split(',')
				ed_list[-1]['tag'] = tags
			elif 'tag:' in line:
				tags = line.strip('tag:')
				tags = tags.strip('\n')
				tags = tags.split(',')
				ed_list[-1]['tag'] = tags

	return_list = list()
	for ed in ed_list:
		e = Entry(file_path, ed['date'], ed['tag'])
		return_list.append(e)

	return return_list

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


def get_entries(entry_list, start_date=None, end_date=None, tags_include=None, tags_exclude=None):

	working_list = entry_list
	if start_date is not None:
		working_list = filter(lambda x: x.date >= start_date, working_list)
	if end_date is not None:
		working_list = filter(lambda x: x.date <= end_date, working_list)

	if tags_include is not None:
		def check_common_tag_inclde(entry_tags):
			# return true if there is a common tag
			for e in entry_tags:
				if e in tags:
					return True
			return False
		working_list = filter(check_common_tag_inclde, entry_list)

	if tags_exclude is not None:
		def check_common_tag_exclude(entry_tags):
			# return false if there is a common tag
			for e in entry_tags:
				if e in tags:
					return False
			return True
		working_list = filter(check_common_tag_exclude, entry_list)	

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

	# colors = [u'white', u'grey']
	# start_of_entry = u'<div style="background-color:{}; padding:20px;">'
	# end_of_entry = u'</div>'

	end_of_entry = u'<img src="{}" style="horizontal-align:middle" />'.format(ENTRY_SEPARATOR_IMG)

	# assemble all texts in html body
	output_txt = u''
	for i in range(0, len(text_list), 2):
		entry_meta = text_list[i]
		entry_meta = entry_meta.splitlines()
		entry_meta = map(lambda x: '<p>{}</p>'.format(x),entry_meta)
		entry_meta = reduce(lambda x,y: x+y, entry_meta)
		entry_meta = to_unicode_or_bust(entry_meta)

		entry_txt = text_list[i+1]
		entry_txt = to_unicode_or_bust(entry_txt)
		entry_txt = pypandoc.convert(entry_txt, 'html', format='md')


		# output_txt = u'{}\n{}\n{}\n{}\n{}\n{}\n'.format(output_txt,
		# 											   start_of_entry.format(colors[i%2]),
		# 											   entry_meta, HLINE_HTML,
		# 											   entry_txt, end_of_entry)

		output_txt = u'{}\n{}\n{}\n{}\n{}\n'.format(output_txt,
													   entry_meta, HLINE_HTML,
													   entry_txt, end_of_entry)

	# output_txt = output_txt.encode('utf-8')
	compile_to_html(output_txt, output_path)

def get_week_entries(entry_list, output_path):
	weekly_last_date = filter(lambda x: 'vecka' in x.tags, entry_list)[-1].date
	week_list = get_entries(entry_list, start_date=weekly_last_date)
	html_from_entries(week_list, output_path)

if __name__ == '__main__':
	# list of absolute paths of all entries
	path_list = list()
	for root, dirs, files in os.walk(JOURNAL_PATH):
		for name in files:
			path_list.append(join(root, name))

	def not_conflicted_copy(string):
		if 'conflicted copy' in string:
			return False
		return True

	# remove conflicted copies form Dropbox
	if DROPBOX_IGNORE_CONFLICTED_COPIES:
		path_list = filter(not_conflicted_copy, path_list)

	entry_list = list()
	for path in path_list:
		entry_list.extend(parse_entries(path))

	entry_list.sort(key=lambda x: x.date)

	#get_week_entries(entry_list, 'week_entries.html')

	#entry_list_file = open('entires.pkl','w')
	#cPickle.dump(entry_list, entry_list_file)

