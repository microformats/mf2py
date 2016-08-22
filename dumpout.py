# coding: utf-8

from mf2py import Parser
import os.path
import glob
import json

allfiles = glob.glob(os.path.join('.', 'tests', 'tests', '**', '**', '*.json'))
for jsonfile in allfiles:
    htmlfile = jsonfile[:-4] + 'html'
    with open(htmlfile) as f:
        p = json.loads(Parser(doc=f).to_json(pretty_print=True))
