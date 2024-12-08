#!/usr/bin/env python3
# ex: set tabstop=4 expandtab:
#
""" Task list program.

AVAILABLE VERBS:

Adding / Editing Tasks:

    add TEXT:
        Add a new todo with text TEXT below the current task.

    adc TEXT:
        Add (see above) followed by cd (see below) to the new task.

    boost PATH [...]:
        Boost the named task(s) to the start of the list

    bump PATH [...]:
        Bump the named task(s) to the end of the list

    by DATE PATH:
        set the deadline for a task

    defer DATE PATH:
        set the start date of a task

    done/undone PATH ...:
        Mark item at each PATH as done or remove mark. Default PATH is current.

    ed PATH text:
        Replace the text of the identified todo item.

    expunge:
        Remove all todos marked as Done from the current task.

    ic:
        Integrity Check. Run this if you are told that a valid path is not
        valid.

    move SRCPATH DSTPATH:
        Move the task identified by SRCPATH to be a child of that identified by
        DSTPATH. NOTE: does not change the referenced task's ID. For that, use
        ren.

    mv SRCPATH DSTPATH:
        Synonym for move.

    mmv SRCPATH ... DSTPATH
        Move multiple items

    ren SRCPATH ID:
        set the ID on the task indicated by SRCPATH. NOTE: cannot move items,
        only set their ID. For that, use mv.

    remain TIME PATH:
        Set the remaining estimated time on a task, or X to remove estimate.

Moving About:

    cd PATH:
        change current task to task at PATH.

    popd:
        Change to the directory at the top of the stack, removing it

    pushd PATH:
        Put the current directory on the top of the stack, and change to the
        specified PATH. If PATH is omitted, perform a pds command (see below)

    rotd:
        pushd, then pop the BOTTOM of the stack.

    swd:
        Switch directory with the top of the directory stack.

    zoom PATH:
        Recursively navigate to the biggest child of the biggest child of the
        identified task.

Display:

    leaves PATH:
        Show the todo items below the PATH that don't themselves have children

    ls PATH:
        List the todo items in the current curdir

    clear:
        clear the screen

    dirs / pds:
        Print directory stack

    pwd:
        Print current task

    show PATH:
        Print the full, unformatted text of the indicated Task.

Reports:

    dump:
        Dump entire database to stdout as a shell script
        (use on commandline, e.g. td dump > restore.sh )

Other Modes:
    batch:
        Useful for restoring dumps, read commands from stdin with no editing
        or readline capability.

    exit (also EOF, also ^D):
        Quit interactive mode.

    interactive:
        This is the default action if no verb is supplied. Enters interactive
        mode where verbs and operands are taken from stdin with history and
        GNU readline.

    help:
        this text

    reset:
        totally don't use this. it resets the database irretrievably

"""
# All code must come after the docstring for __doc__ to work.
GIT_DESCRIPTION = "(development version)"

import colorama
from copy import copy
import os
import pickle
import argparse

try:
    import readline
except ImportError:
    readline = None
import sys
import time

import working_hours

colorama.init( )
ANSI_RED = "\033[31;1m"
ANSI_GREEN = "\033[32;1m"
ANSI_BRIGHT = "\033[1m"
ANSI_RESET = "\033[0m"

VERBS = {
    "add": [ "TEXT" ],
    "adc": [ "TEXT" ],
    "batch": [ ],
    "boost": [ "PATH" ],
    "bump": [ "PATH" ],
    "by": [ "DATE", "PATH" ],
    "cd": [ "PATH" ],
    "clear": [ ],
    "defer": [ "DATE", "PATH" ],
    "dirs": [ ],
    "done": [ "PATH" ],
    "dump": [ ],
    "ed": [ "PATH", "TEXT" ],
    "expunge": [ ],
    "help": [ ],
    "ic": [ ],
    "interactive": [ ],
    "ls": [ ],
    "mv": [ "SRCPATH", "DSTPATH" ],
    "mmv": [ "SRCPATHS", "DSTPATH" ],
    "pds": [ ],
    "popd": [ ],
    "pushd": [ "PATH" ],
    "pwd": [ ],
    "ren": [ "SRCPATH", "ID" ],
    "remain": [ "TIME", "PATH" ],
    "reset": [ ],
    "rotd": [ ],
    "show": [ "PATH" ],
    "swd": [ ],
    "undone": [ "PATH" ],
}

EXE_NAME = "td"
COLUMNS = int( os.environ.get( 'COLUMNS', '80' ) )
TASK_TEXT_WIDTH = COLUMNS - 18
PROMPT = EXE_NAME + '> '
ID_WIDTH = 4
DEFAULT_REMAIN = 4.0

# global_db is used for readline to be able to hook into the Todo list.
global_db = None


def warn( s ):
    sys.stderr.write( "Warn: %s\n" % s )


def error( s ):
    sys.stderr.write( "Error: %s\n" % s )


def pretty_time( seconds ):
    thresholds = [ ( 60, 'm'), ( 60, 'h' ), ( 24, 'd' ), ( 7, 'w' ) ]
    n = seconds
    ret = 's'
    for thres, unit in thresholds:
        ret = '%d%s' % ( n % thres, ret )
        n = n // thres
        if n == 0:
            return ret
        else:
            ret = "%s, %s" % ( unit, ret )


def chomp_word( sentence ):
    try:
        space = sentence.index( " " )
    except ValueError:
        return sentence, ""
    return ( sentence[ :space ], sentence[ space + 1: ].strip( ) )


def banner( ch=None ):
    if ch is None:
        ch = "="
    return ANSI_GREEN + ( ch * ( COLUMNS - 1 ) ) + ANSI_RESET


class TaskDatabase( object ):
    def __init__( self ):
        """ Initialize a new TaskDatabase containing the root task. """
        self.root = Task( self, "todo", "/ Task List" )
        self.root.parent = self.root
        self.curdir = self.root
        # Dirstack is the stack of directories for pushd and popd.
        self.dirstack = [ ]
        self.path = [ ]

    def add( self, text, path=None ):
        """ Add a task to the current dir """
        if path is None:
            path = "."
        return self.get( path ).add( text )

    def get( self, path, origin=None ):
        """ resolve a path and return the task found there. """
        if origin is None:
            origin = self.curdir
        if path == '':
            return origin
        else:
            plist = path.split( '/' )
            head = plist[ 0 ]
            tail = '/'.join( plist[ 1: ] )
            if head == '':  # path started with /
                return self.get( tail, self.root )
            elif head == '.':
                return self.get( tail, origin )
            elif head == '..':
                return self.get( tail, origin.parent )
            elif origin.get_child( head ):
                return self.get( tail, origin.get_child( head ) )
            else:
                return None

    def cd( self, path ):
        """ resolve path and change current directory to it. """
        tgt = self.get( path )
        if tgt is None:
            error( "Invalid Path" )
            return False
        else:
            self.curdir = tgt
            return True

    def pds( self ):
        """ print the directory stack """
        things = map( Task.get_path,
                      [ self.curdir ] + [ x
                                          for x in reversed( self.dirstack ) ] )
        print (', '.join( things ))

    def pushd( self, path ):
        """ push directory onto stack and change """
        olddir = self.curdir
        if self.cd( path ):
            self.dirstack.append( olddir )
            self.pds( )

    def popd( self ):
        """ pop directory from stack """
        if len( self.dirstack ) == 0:
            error( "No more paths to pop." )
        else:
            self.cd( self.dirstack.pop( ).get_path( ) )

    def rotd( self ):
        """ pushd and unqueue current dir from BOTTOM of stack
        """
        if len( self.dirstack ) == 0:
            error( "No more paths to pop." )
        else:
            dest = self.dirstack.pop( 0 ).get_path( )
            self.pushd( dest )

    def swd( self, num ):
        """ switch directory (exchange current directory with the one on the
            top of the stack, or with one by index if specfied
        """
        if isinstance( num, int ):
            pass
        elif num.isdigit( ):
            num = int( num )
        else:
            num = 1
        if len( self.dirstack ) < num:
            error( "Dir Stack has %d element(s)." % len( self.dirstack ) )
            return False
        else:
            tmp = self.dirstack[ -num ]
            self.dirstack[ -num ] = self.curdir
            self.curdir = tmp
            return True

    def ls( self, path='.' ):
        """ resolve path and display the resulting task """
        tgt = self.get( path )
        if tgt is None:
            error( "Invalid Path" )
        else:
            tgt.ls( )

    def dump( self ):
        print ("td batch <<EOF")
        print ("reset")
        self.root.dump( )
        print ("EOF")


class Task( object ):
    def __init__( self, parent, text, category=None, prio=1, due=None ):
        """ initialize a new task under a parent """
        self.parent = parent
        # We magic the ID. Our parent will check it and modify if necessary.
        self.set_id( text )
        self.text = text
        self.prio = prio
        self.due = due
        self.done = None
        self.children = [ ]
        self.remain = None
        self.created = time.time( )
        self.deadline = None
        self.defer = None
        self.expanded = False

    def add( self, text ):
        """ create and add a child task given its text """
        if text.strip( ) == "":
            return None
        return self.add_child( Task( self, text ) )

    def add_child( self, t, id=None ):
        """ add an existing child task to a task, adjusting its ID if necessary """
        # Allow caller to suggest the ID
        if id is not None:
            t.set_id( id )
        else:
            t.set_id( t.get_id( ) )  # force a validation of ID

        orig_id = t.get_id( )  # the desired ID
        count = 0
        while self.get_child( t.get_id( ) ) is not None:  # now disambiguate.
            count = count + 1
            sc = str( count )
            wid = len( sc )
            t.set_id( orig_id[ :ID_WIDTH - wid ] + sc )
        # the task's ID is unique amongst its new siblings. Move it.
        self.children.append( t )
        t.parent = self
        return t

    def boost( self ):
        """ move self to start of parent's list of children """
        self.parent.children = [ self ] + [ c for c in self.parent.children if c is not self ]

    def bump( self ):
        """ move self to end of parent's list of children """
        self.parent.children = [ c for c in self.parent.children if c is not self ]
        self.parent.children.append( self )

    def calc_deadline( self ):
        """ set deadline to date/time dt """
        if self.deadline is None:
            return self.parent.calc_deadline( )
        else:
            return self.deadline

    def calc_remain( self, override=True ):
        """ return the remain calculated recursively.

            override:   return the user-set remain if it's more than the
                        calculated remain. Default True
        """
        if self.done is not None:
            return 0.0
        else:
            found = False
            total = 0.0
            for c in self.children:
                if c.done is None:
                    found = True
                    total += c.calc_remain( )
            if found:
                if self.remain is None or ((self.remain < total) or not override):
                    return total
                else:
                    return self.remain
            else:
                if self.remain is not None:
                    return self.remain
                else:
                    return DEFAULT_REMAIN

    def count_tasks( self ):
        """ return the number of live tasks this task represents """
        if len( self.children ) == 0:
            return 1
        else:
            return sum( c.count_tasks( ) for c in self.children )

    def dump( self, depth=None ):
        """ recursive dump of the commands necessary to reproduce this task
            and all its descendents
        """
        INDENT = "  "
        if depth is None:
            depth = 0
        print (INDENT * depth + "# " + self.get_path( ))
        if self.get_path( ) == '/':
            print ("ed / " + self.text)
        else:
            print (INDENT * depth + "adc %s" % self.text)
            depth = depth + 1
            print (INDENT * depth + "ren . %s" % self.get_id( ))
            if self.remain is not None:
                print (INDENT * depth + "remain %.2f" % self.remain)
        for c in self.children:
            c.dump( depth )
        if self.get_path( ) != '/':
            if self.done is not None:
                print (INDENT * depth + "done .")
            else:
                print (INDENT * depth + "cd ..")
            depth -= 1
            print (INDENT * depth + "# End of %s. " % self.get_path( ))

    def expand( self ):
        self.expanded = True

    def expunge( self ):
        """ remove all children marked as done """
        self.children = [ c for c in self.children if c.done is None ]

    def format( self, task_text_width=None, highlight=None, with_path=None, prefix=None ):
        """ format this task on one line for output """
        if task_text_width is None:
            task_text_width = TASK_TEXT_WIDTH
        if with_path is None:
            with_path = False
        if prefix is None:
            prefix = ''

        if self.deadline is not None:
            task_text_width -= 10  # width of "mm/dd XXX "
        if highlight is None:
            highlight = False
        ret = ""
        if with_path:
            ret += self.get_path( )
            task_text_width -= len( self.get_path( ) )
        if not self.match_id( self.text ):
            formatted_id = "%s: " % self.get_id( )
            ret += formatted_id
            task_text_width -= len( formatted_id )
        ret = prefix + ret
        task_text_width -= len( prefix )

        ret += ("%-" + str( task_text_width ) + "s ") % self.text[ :task_text_width ]

        if self.deadline is not None:
            ret += self.deadline.strftime( "%d/%m " ) + ("%03d " % working_hours.working_hours_till( self.deadline ) )

        calcd_remain = self.calc_remain( False )
        tail = ''
        if self.done is None:
            if self.remain is None:
                ret += "   -.--"
            else:
                if calcd_remain > (self.remain * 1.02):  # effort overrun in red
                    ret += ANSI_RED
                    tail = ANSI_RESET
                elif calcd_remain < (self.remain * 0.75):  # effort underrun by 75% green
                    ret += ANSI_GREEN
                    tail = ANSI_RESET
                ret += "% 7.2f" % self.remain
        else:
            ret += "   Done"
        ret += "% 7.2f " % calcd_remain
        ret += tail
        if len( self.children ) > 0 and self.done is not None:
            ret += "*"
        elif len( self.children ) > 0:
            ret += "+"
        elif self.done is not None:
            ret += "X"
        else:
            ret += " "

        if highlight:
            ret = ANSI_BRIGHT + ret + ANSI_RESET
        return ret

    def get_child( self, key ):
        """ retrieve the child with the given key, or return None """

        if key == "@":
            if len( self.children ) > 0:
                # commercial at means 'get first non-done'
                for c in self.children:
                    if c.done is None:
                        return c
            # They must mean me if there are no (undone) children.
            return self

        for c in self.children:
            if c.match_id( key ):
                return c
        # not found
        return None

    def get_id( self ):
        """ retrieve the (tidied?) ID of this task """
        if isinstance( self.task_id, int ):
            return "#%03d" % self.task_id
        else:
            return self.task_id

    def get_path( self ):
        """ return the absolute path of this task """
        if self.parent == self:
            return "/"
        else:
            return self.parent.get_path( ) + str( self.task_id ) + "/"

    def integrity_check( self, recurse=True ):
        """ re-write the list of children so that they have valid IDs. Recurse """
        msgs = [ ]
        childlist = copy( self.children )
        del self.children[ : ]
        for c in childlist:
            self.add_child( c )
            if recurse:
                msgs.extend( c.integrity_check( True ) )
        return msgs

    def leaves( self ):
        """ descend this task and show its leaf descendents """
        if len( [ x for x in self.children if x.done is None ] ) == 0:
            print( self.format( TASK_TEXT_WIDTH, with_path=True ))
        else:
            for c in self.children:
                if c.done is None:
                    c.leaves( )

    def ls( self, prefix="" ):
        """ show this task and its children if any """
        if prefix == "":
            depth = self.print_lineage( self )
            print (banner( '-' ))
        undones = [ c for c in self.children if c.done is None ]
        dones = [ c for c in self.children if c.done is not None ]
        for d in undones:
            print( d.format( TASK_TEXT_WIDTH, highlight=True, prefix=prefix ))
            if d.expanded:
                d.ls( prefix + '    /' )
        for d in dones:
            print( d.format( TASK_TEXT_WIDTH, highlight=False, prefix=prefix ))
        if prefix == "":
            print( banner( ))

    def match_id( self, m ):
        """ return whether the given id identifies this Task """
        id = self.get_id( )
        return m[ :len( id ) ].lower( ) == id.lower( )

    def print_lineage( self, highlight=None ):
        if self.parent == self:  # then I am root
            print (banner( ))
            print( self.text, GIT_DESCRIPTION)
            return ""
        else:
            dep = self.parent.print_lineage( highlight )
            print( dep + self.format( TASK_TEXT_WIDTH - len( dep ), highlight == self ))
            return "  " + dep

    def rm( self, id ):
        """ remove the child identified by id """
        self.children.remove( self.get_child( id ) )

    def set_id( self, id ):
        """ set the task's ID. This function is concerned with validating and
            formatting the ID, but not with making sure the parent's index is
            correct.  That has to be the parent's concern.
            """
        if isinstance( id, int ):
            self.task_id = "#%03d" % id
        else:
            id = id.replace( " ", "" ).replace( "/", "" ).lower( )[ :ID_WIDTH ]
            if id.isdigit( ):
                self.task_id = ("#%03d" % int( id ) )
            else:
                self.task_id = id

    def set_remain( self, days ):
        """ set the estimated time remaining on this task
            Argument is number or None"""
        self.remain = days

    def set_text( self, text ):
        """ set the text for the task """
        self.text = text

    def max_depth( self ):
        md = 1
        for c in self.children:
            if c.done is None:
                cmd = c.max_depth( )
                if md <= cmd:
                    md = cmd + 1
        return md

    def unexpand( self ):
        self.expanded = False

    def zoom( self ):
        """ descend recursively into the child with the most remaining time.
        """
        if len( self.children ) == 0:
            return self
        else:
            min = self.calc_remain( )
            max = 0.0
            for c in self.children:
                r = c.calc_remain( )
                if r > max:
                    result = c
                    max = r
                if r < min:
                    min = r
            if max == min:
                return self
            else:
                return result.zoom( )


def read_input( prompt ):
    """ issue the prompt and read input, returning None if
            * EOF
            * ^D
            * exit is typed
    """
    try:
        l = input( prompt )
        if l == '\04':
            return None
        if l == 'exit':
            return None
    except EOFError:
        return None
    return l

def execute_command( command_line ):
    """ one action upon the database. (which of course may be "interactive",
        in which case it loops and recurses on itself.
    """
    # We assume we will re-write the database after we're done with the command
    save = True

    # Wa assume we have successfully executed the command unless we hear otherwise
    success = True

    # break off the first word as our command
    command, operand = chomp_word( command_line )

    # See whether we can/should read the database
    if command[ 0 ] == '#':  # Special case: skip comments
        save = False
        return True

    elif command == 'reset':
        info( "cleared TODO database." )
        db = TaskDatabase( )

    elif command == 'batch':
        pass  # batch will attempt the load
        save = False

    elif command == 'interactive':
        pass  # interactive will attempt the load
        save = False

    else:
        try:
            f = open( PICKLE_FILE, "rb" )
            db = pickle.load( f )
            global_db = db
            f.close( )
        except:
            warn( "could not load %s." % PICKLE_FILE )
            db = TaskDatabase( )

    # Interpret the command
    if command == 'help':
        print (__doc__)

    elif command == 'add':  # Add a task in the current curdir
        print( db.add( operand ).task_id)

    elif command == 'adc':  # Add task and change to it.
        db.cd( db.add( operand ).get_path( ) )

    elif command == 'batch':
        l = sys.stdin.readline( )  # we don't strip() it here, because then blank line terminates the while loop
        while l:
            if l.strip( ) != '':
                if not execute_command( l.strip( ) ):
                    success = False
                    break
            l = sys.stdin.readline( )
        print ("<EOF>")

    elif command == 'boost':
        success = True
        srcs = [ ]
        while success and len( operand.strip( ) ) > 0:
            src_path, operand = chomp_word( operand )
            src = db.get( src_path )
            if src is None:
                error( "Invalid Path: %s" % src_path )
                success = False
            srcs.append( src )
        if success:
            for tgt in reversed( srcs ):
                tgt.boost( )

    elif command == 'bump':
        success = True
        srcs = [ ]
        while success and len( operand.strip( ) ) > 0:
            src_path, operand = chomp_word( operand )
            src = db.get( src_path )
            if src is None:
                error( "Invalid Path: %s" % src_path )
                success = False
            srcs.append( src )
        if success:
            for tgt in srcs:
                tgt.bump( )

    elif command == 'by':
        date_text, path = chomp_word( operand )
        try:
            dt = working_hours.parse_date( date_text )
        except:
            error( "Invalid Date" )
            return False
        tgt = db.get( path )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            tgt.deadline = dt

    elif command == 'cd':
        db.cd( operand )

    elif command == 'clear':
        print( '\x1b[H\x1b[2J')

    elif command == 'defer':
        date_text, path = chomp_word( operand )
        try:
            dt = working_hours.parse_date( date_text )
        except:
            error( "Invalid Date" )
            return False
        tgt = db.get( path )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            tgt.defer( dt )

    elif command == 'done':
        if operand == '':
            error( "Missing Path" )
            success = False
        else:
            cd_dot_dot = False
            while operand != "":
                path, operand = chomp_word( operand )
                tgt = db.get( path )
                if tgt is None:
                    error( "Invalid Path (%s)" % path )
                    success = False
                else:
                    tgt.done = time.time( )
                    if tgt == db.curdir:
                        cd_dot_dot = True
            if cd_dot_dot:
                db.cd( '..' )

    elif command == 'dump':  # spit out the whole database as a program that re-creates it
        db.dump( )

    elif command == 'ed':  # edit the item at path to have text x
        path, text = chomp_word( operand )
        tgt = db.get( path )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            tgt.set_text( text )

    elif command == 'expand':
        tgt = db.get( operand )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            tgt.expand( )

    elif command == 'expunge':
        tgt = db.get( operand )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            tgt.expunge( )

    elif command == 'ic':
        log = db.root.integrity_check( )
        for l in log:
            print (l)
        print( "check complete.")

    elif command == 'interactive':
        execute_command( 'ls' )
        l = read_input( PROMPT )
        while l is not None:
            if l.strip() != '':
                success = execute_command( l.strip() ) and success
            l = read_input( PROMPT )
        print ("<EOF>")

    elif command == 'leaves':  # No command line==Display the tasks
        tgt = db.get( operand )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            tgt.leaves( )

    elif command == 'ls':  # No command line==Display the tasks
        tgt = db.get( operand )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            tgt.ls( )

    elif command == 'mv' or command == 'move':
        src_path, text = chomp_word( operand )
        src = db.get( src_path )
        if src is None:
            error( "Invalid Source Path" )
            success = False
        elif src.parent == src:
            error( "Can't move the root!" )
            success = False
        else:
            tgt_path, text = chomp_word( text )
            tgt = db.get( tgt_path )
            if tgt is None:
                error( "Invalid Target Path" )
                success = False
            else:
                print ("from: %s" % src.get_path( ))
                src.parent.rm( src.get_id( ) )
                tgt.add_child( src )
                print( "to: %s" % src.get_path( ))
    elif command == 'mmv':  # multi move
        srcs = [ ]
        while success and len( operand.strip( ) ) > 0:
            src_path, operand = chomp_word( operand )
            src = db.get( src_path )
            if len( operand.strip( ) ) > 0:
                # queue up the task to move
                if src is None:
                    error( "Invalid Source Path" )
                    success = False
                elif src.parent == src:
                    error( "Can't move the root!" )
                    success = False
                srcs.append( src )
            else:
                # Now move the things to the target
                tgt = src
                if tgt is None:
                    error( "Invalid Target Path" )
                    success = False
                else:
                    if len( srcs ) == 0:
                        error( "Missing Destination Path" )
                        success = False
                    else:
                        for src in srcs:
                            src_path = src.get_path( )
                            src.parent.rm( src.get_id( ) )
                            tgt.add_child( src )
                            print( "from: %s to %s." % ( src_path, src.get_path( ) ))

    elif command == 'pds':
        db.pds( )

    elif command == 'dirs':  # synonym for pds
        db.pds( )

    elif command == 'pushd':
        if operand == '':
            db.pds( )
        else:
            db.pushd( operand )

    elif command == 'popd':
        db.popd( )
        db.pds( )

    elif command == 'pwd':
        print (db.curdir.get_path( ))

    elif command == 'reset':  # We've already done the action but don't want to land in the else:
        pass

    elif command == 'remain':
        days, path = chomp_word( operand )
        tgt = db.get( path )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            if days == "X":
                tgt.set_remain( None )
            else:
                try:
                    tgt.set_remain( float( days ) )
                except ValueError:
                    error( "Remain TIME should be float or X." )

    elif command == 'ren':
        srcname, remains = chomp_word( operand )
        dstname, remains = chomp_word( remains )
        tgt = db.get( srcname )
        tgt2 = db.get( dstname )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        elif tgt2 is not None:
            error( "Destination ID '%s' already exists" % dstname )
            success = False
        else:
            tgt.set_id( dstname )
            tgt.parent.integrity_check( False )

    elif command == 'rotd':
        db.rotd( )

    elif command == 'show':
        tgt = db.get( operand )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            print( tgt.text)

    elif command == 'swd':
        if db.swd( operand ):
            db.pds( )

    elif command == 'undone':
        cd_dot_dot = False
        while operand != "":
            path, operand = chomp_word( operand )
            tgt = db.get( path )
            if tgt is None:
                error( "Invalid Path (%s)" % path )
                success = False
            else:
                tgt.done = None

    elif command == 'unexpand':
        tgt = db.get( operand )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            tgt.unexpand( )

    elif command == 'version':
        print (GIT_DESCRIPTION)

    elif command == 'zoom':
        tgt = db.get( operand )
        if tgt is None:
            error( "Invalid Path" )
            success = False
        else:
            db.cd( tgt.zoom( ).get_path( ) )

    else:
        error( "unknown verb %s." % command )
        success = False
    if save:
        f = open( PICKLE_FILE, "wb" )
        pickle.dump( db, f )
        f.close( )

    return success


def find_config_file( requested_path, default_path ):
    """ If requested_path indicates a file, use it.
        elif requested_path is a non-existent name under an existing directory, create and use that
        elif requested_path is a directory, create or use .pytask.pickle in that dir
        else
            search from current dir up to root
            if not found, use default_path
    """
    if os.path.isdir( requested_path ):
        return os.path.join( requested_path, '.pytask.pickle' )
    elif requested_path != '' and os.path.isdir( os.path.abspath( os.path.join( requested_path, '..' ) ) ):
        return requested_path
    else:
        path = os.getcwd( )
        while path != os.path.abspath( '/' ):
            candidate = os.path.join( path, '.pytask.pickle' )
            if os.path.isfile( candidate ):
                return candidate
            path = os.path.abspath( path + '/..' )
        return os.path.abspath( os.path.expanduser( os.path.join( default_path, ".pytask.pickle" ) ) )


def get_arguments( ):
    ap = argparse.ArgumentParser( )
    ap.add_argument( '--pickle-file', '-f', help='Specify the path of the picklefile or its containing dir.',
                     default='' )
    ap.add_argument( '--verbose', '-v', action='store_true', help='Write some light diagnostic info to stderr' )
    ap.add_argument( 'text', nargs='*', help='command and arguments' )
    return ap.parse_args( )


if __name__ == "__main__":
    args = get_arguments( )
    if args.pickle_file != '':
        args.pickle_file = os.path.abspath( os.path.expanduser( args.pickle_file ) )

    PICKLE_FILE = find_config_file( args.pickle_file, os.environ.get( 'TD_PICKLE_PATH', '~' ) )
    if args.verbose:
        sys.stderr.write( "PICKLE_FILE = %s\n" % PICKLE_FILE )

    HISTORY_FILE = os.path.expanduser( "~/.pytask.history" )

    # if we are not given a commandline, then go into interactive mode
    if len( args.text ) == 0:
        command_line = 'interactive'
    else:
        command_line = ' '.join( args.text )

    # Set up readline in case we need it
    try:
        # readline.set_completer( auto_complete )
        # readline.parse_and_bind( "tab: complete" )
        readline.read_history_file( HISTORY_FILE )
    except:
        pass

    # then execute it
    execute_command( command_line )
    execute_command( 'show @' )

    try:
        readline.write_history_file( HISTORY_FILE )
    except:
        pass

