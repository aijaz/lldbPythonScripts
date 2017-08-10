#!/usr/bin/python

import stripQuotes

def format (valobj,internal_dict):
    """valobj: an SBValue which you want to provide a summary for
       internal_dict: an LLDB support object not to be used"""
    t = valobj.GetChildMemberWithName('title')
    n = valobj.GetChildMemberWithName('speaker').GetChildMemberWithName('name')
    return stripQuotes.strip(t.GetObjectDescription()) + " by " + stripQuotes.strip(n.GetObjectDescription())


def __lldb_init_module(debugger, dict):
    # This initializer is being run from LLDB in the embedded command interpreter
    # Make the options so we can generate the help text for the new LLDB
    # command line command prior to registering it with LLDB below
    # Add any commands contained in this module to LLDB
    debugger.HandleCommand('type summary add --python-function sessionFormatter.format MyConf.Session')
    print 'The formatter for MyConf.Session has been set up.'
