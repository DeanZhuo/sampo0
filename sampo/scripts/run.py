
import sys, os
import argparse

from rhombus.scripts.run import main as rhombus_main, set_config
from rhombus.lib.utils import cout, cerr, cexit

from sampo.models.handler import DBHandler

def greet():
    cerr('command line utility for sampo')


def usage():
    cerr('sampo-run - command line utility for sampo')
    cerr('usage:')
    cerr('\t%s scriptname [options]' % sys.argv[0])
    sys.exit(0)


set_config( environ='RHOMBUS_CONFIG',
            paths = ['sampo.scripts.'],
            greet = greet,
            usage = usage,
            dbhandler_class = DBHandler,
            includes = ['sampo.includes'],
)

main = rhombus_main



