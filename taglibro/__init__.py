from flask import Flask
from taglibro.taglibro import get_entry_list
import taglibro.config

app = Flask('taglibro')

import taglibro.views
