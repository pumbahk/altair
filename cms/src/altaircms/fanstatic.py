from js.jquery import jquery
from js.underscore import underscore
from js.jquery_tools import jquery_tools
from js.json2 import json2
from js.jqueryui import black_tie
from js.jqueryui import jqueryui
from js.tinymce import tinymce

def jqueries_need():
    underscore.need()
    jquery.need()
    jquery_tools.need()
    json2.need()
    jqueryui.need()
    black_tie.need()

def wysiwyg_editor_need():
    tinymce.need()
