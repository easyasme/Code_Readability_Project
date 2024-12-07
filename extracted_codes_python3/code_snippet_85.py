#!/usr/bin/env python
import argparse
import PersonalBacklog
import re
import readline
import sys
from cmd import Cmd

if sys.version_info.major < 3:
    exit("Python 3 is required")

class MyPrompt(Cmd):
    prompt = 'pb> '
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, inp):
        '''exit the application. Shorthand: x q.'''
        print("Bye")
        return True

    def do_add(self, inp):
        '''
            Add task.
            Will ask for title, estimate, and priority.
        '''
        title = input("Task Title: ")
        estimate = input("Estimate (1, 2, 3, 5, 8, 13, 21, 34, 55): ")
        priority = input("Priority (0 = now, x = max time, some number): ")
        ret = self.pb.add(title, estimate, priority)
        if 'error' in ret:
            print(ret['error'])


    def do_cal(self, inp):
        '''Show calendar
           cal      (default = today)
           cal 0    (today)
           cal 1    (tomorrow)
           cal 2    (2 days from now)
           cal -1   (yesterday)
        '''
        if inp == '':
            inp = '0'
        ret = self.pb.list_calendar(inp)
        if 'error' in ret:
            print(ret['error'])

    def do_delete(self, inp):
        '''
        delete a TODO item.
        It accepts a number from the 'list' command.
        '''
        ret = self.pb.delete(inp)
        if 'error' in ret:
            print(ret['error'])

    def do_edit(self, inp):
        '''
        edit entry from a 'list'
        '''
#        m = re.search('\A(\d+)\Z', choice)
        entry = self.pb.get(inp)
        if 'error' in entry:
            print(entry['error'])
        else:
            entry["title"] = input_with_prefill("edit title> ", entry["title"])
            self.pb.update(inp, entry)


    def do_list(self, inp):
        '''
        List TODO items
        '''
        self.pb.list_todo()

    def do_schedule(self, inp):
        '''
        Schedule: add a calendar entry
        '''
        title = input("Schedule Title: ")
        start_date = input("Start Date YYYY-MM-DD 0=today 1=tomorrow: ")
        start_time = input("Start time HH:MM: ")
        end_date   = input("End Date YYYY-MM-DD ENTER=same as start date")
        end_time   = input("End time HH::MM: ")
        location   = input("Location (free text): ")
        ret = self.pb.schedule(title, start_date, start_time, end_date, end_time, location)
        if 'error' in ret:
            print(ret['error'])

    def default(self, inp):
        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)

        if re.search('\A\d+\s', inp):
            self.pb.process_cli(inp)

        print("Unhandled command: {}".format(inp))


def input_with_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result

def main():
    arp = argparse.ArgumentParser()
    arp.add_argument("file", help="Name of the JSON file which is our 'database'")
    args = arp.parse_args()

    cli = MyPrompt()
    cli.pb = PersonalBacklog.PB(args.file)
    cli.cmdloop()



if __name__ == '__main__':
    main()

