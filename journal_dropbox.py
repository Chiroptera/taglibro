
import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

from config import Config

DROPBOX_ACCESS_TOKEN = 'UqWYTaD1FakAAAAAAAAMk-Qtyh3qc-nT-EGEkmEG-K7_LLxblxNPD626T5D3ARhb'

'''structure:
new_entries (folder) : for putting new, unprocessed new_entries
journal (folder) : for keeping all entries organized by year/month; all entries filenames will start with the date followed by an ID for the particular entry.
journal.cfg : configuration files
index : dictionary with metadata about all organized entries - used for search, retrieval, etc.
'''

class JournalAccess:
	'''This is supposed to be a generic class to be implemented for different services, e.g. Dropbox, local, etc.'''
	def __init__():
		pass

	def addEntry():
		pass

	def reviewWeek():
		pass

	def reviewMonth():
		pass

	def reviewYear():
		pass

	def getEntries(start_date, end_date, tags):
		pass

class DropboxJournal(JournalAccess):
	def connect(token):
	    # Create an instance of a Dropbox class, which can make requests to the API.
	    dbx = dropbox.Dropbox(token)

	    # Check that the access token is valid
	    try:
	        dbx.users_get_current_account()
	    except AuthError as err:
	        sys.exit("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
	    return dbx


if __name__ == '__main__':
	print('Doing nothing.')