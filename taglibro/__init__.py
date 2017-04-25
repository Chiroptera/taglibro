from flask import Flask
from taglibro.taglibro import get_entry_list

app = Flask('taglibro')

import taglibro.views
