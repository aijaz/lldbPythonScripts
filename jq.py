#!/usr/bin/python

#----------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
#
# # To use this in the embedded python interpreter using "lldb" just
# import it with the full path using the "command script import"
# command
#   (lldb) command script import /path/to/cmdtemplate.py
#----------------------------------------------------------------------

import lldb
import commands
import optparse
import shlex
from subprocess import Popen, PIPE, STDOUT



def create_jq_options():
    usage = "usage: %prog [options] <jq_filter> <variable_name>"
    description = '''This command will run the jq using jq_filter on the
NSString variable_name, which is expected to contain valid JSON. As a
side effect, the JSON contained in variable_name will be saved in
/tmp/jq_json and the filter will be saved in /tmp/jq_prog.
'''
    parser = optparse.OptionParser(
        description=description,
        prog='jq',
        usage=usage)
    parser.add_option(
        '-c',
        '--compact',
        action='store_true',
        dest='compact',
        help='compact instead of pretty-printed output',
        default=False)
    parser.add_option(
        '-S',
        '--sort',
        action='store_true',
        dest='sort',
        help='sort keys of objects on output',
        default=False)
    return parser


def jq_command(debugger, command, result, dict):
    # Use the Shell Lexer to properly parse up command options just like a
    # shell would
    
    jq_exe = "/Users/aijaz/local/bin/jq"
    jq_prog_file = "/tmp/jq_prog"
    jq_json_file = "/tmp/jq_json"

    command_args = shlex.split(command)
    parser = create_jq_options()
    try:
        (options, args) = parser.parse_args(command_args)
    except:
        # if you don't handle exceptions, passing an incorrect argument to the OptionParser will cause LLDB to exit
        # (courtesy of OptParse dealing with argument errors by throwing SystemExit)
        result.SetError("option parsing failed")
        return

    # in a command - the lldb.* convenience variables are not to be used
    # and their values (if any) are undefined
    # this is the best practice to access those objects from within a command
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    if not frame.IsValid():
        return "no frame here"

    jq_prog = args[0]
    val = frame.var(args[1])
    val_string = val.GetObjectDescription()

    f = open(jq_json_file, 'w')
    f.write(val_string)
    f.close()

    f = open(jq_prog_file, 'w')
    f.write(jq_prog)
    f.close()

    compact = ""
    sort = ""

    if options.compact :
        compact = "-c"

    if options.sort :
        sort = "-S"

    print >>result, (commands.getoutput("%s %s %s -f %s %s" % (jq_exe, compact, sort, jq_prog_file, jq_json_file) ))


def __lldb_init_module(debugger, dict):
    # This initializer is being run from LLDB in the embedded command interpreter
    # Make the options so we can generate the help text for the new LLDB
    # command line command prior to registering it with LLDB below
    parser = create_jq_options()
    jq_command.__doc__ = parser.format_help()
    # Add any commands contained in this module to LLDB
    debugger.HandleCommand(
        'command script add -f jq.jq_command jq')
    print 'The "jq" command has been installed, type "help jq" or "jq --help" for detailed help.'
