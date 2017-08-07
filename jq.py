#!/usr/bin/python

#----------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
#
# # To use this in the embedded python interpreter using "lldb" just
# import it with the full path using the "command script import"
# command
#   (lldb) command script import /path/to/file.py
#
# Inspired by 
# http://llvm.org/svn/llvm-project/lldb/trunk/examples/python/cmdtemplate.py
# 
# For a blog post describing this, visit 
# http://aijazansari.com/2017/01/11/lldb-python/
#----------------------------------------------------------------------

import lldb
import commands
import optparse
import shlex

def create_jq_options():
    """Parse the options passed to the command. 
    Also provides the description string that's used as
    the command's help string.
    """
    usage = "usage: %prog [options] <jq_filter> <variable_name>"
    description = '''This command will run the jq using jq_filter on the
NSString local variable variable_name, which is expected to contain valid JSON. 
As a side effect, the JSON contained in variable_name will be saved in
/tmp/jq_json and the filter will be saved in /tmp/jq_prog.

Example:
%prog '.[]|{firstName, lastName}' jsonStr
%prog '.[]|select(.id=="f9a5282e-523f-4b83-a6ca-566e3746a4c7").schools[1].\
school.mainLocation.address.city' body
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
        '-n',
        '--nsstring',
        action='store_true',
        dest='nsstring',
        help='Use this option if the variable is an NNSString. Omit it if it is a Swift String'
        default=False)
    parser.add_option(
        '-S',
        '--sort',
        action='store_true',
        dest='sort',
        help='sort keys of objects on output',
        default=False)
    return parser


# The actual python function that is bound to the lldb command.
def jq_command(debugger, command, result, dict):
    # path to the jq executable. This is the only variable you need to change
    jq_exe = "/Users/aijaz/local/bin/jq"

    # the filter will be written to this file and will be invoked via jq -f
    # The benefit of saving the filter in a file is that we don't have to
    # worry about escaping special characters.
    jq_prog_file = "/tmp/jq_prog"

    # the value of the NSString variable will be saved in this file
    # jq will be invoked on the file, not using stdin
    # For some reason, large amounts of data were causing the lldb
    # rpc server to crash when using stdin
    jq_json_file = "/tmp/jq_json"

    # Use the Shell Lexer to properly parse up command options just like a
    # shell would
    command_args = shlex.split(command)
    parser = create_jq_options()
    try:
        (options, args) = parser.parse_args(command_args)
    except:
        # if you don't handle exceptions, passing an incorrect argument to the 
        # OptionParser will cause LLDB to exit (courtesy of OptParse dealing 
        # with argument errors by throwing SystemExit)
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

    # The command is called like "jq '.' val"
    # . is the jq program
    # val is the name of the variable
    # val_string is the value of the variable
    jq_prog = args[0]
    val = frame.var(args[1])
    if options.nsstring:
        val_string = val.GetObjectDescription()
    else :
        val_string = eval(val.GetObjectDescription())


    # write the json file and jq program to temp files
    f = open(jq_json_file, 'w')
    f.write(val_string)
    f.close()

    f = open(jq_prog_file, 'w')
    f.write(jq_prog)
    f.close()

    # default values of the option placeholders
    compact = ""
    sort = ""

    if options.compact :
        compact = "-c"

    if options.sort :
        sort = "-S"

    # invoke jq and print the output to the result variable
    print >>result, (commands.getoutput("%s %s %s -f %s %s" % (
        jq_exe, compact, sort, jq_prog_file, jq_json_file) ))

    # not returning anything is akin to returning success


def __lldb_init_module(debugger, dict):
    # This initializer is being run from LLDB in the embedded command interpreter
    # Make the options so we can generate the help text for the new LLDB
    # command line command prior to registering it with LLDB below
    parser = create_jq_options()
    jq_command.__doc__ = parser.format_help()

    # Add any commands contained in this module to LLDB
    debugger.HandleCommand('command script add -f jq.jq_command jq')

    print """The "jq" command has been installed, \
type "help jq" or "jq --help" for detailed help.\
"""
