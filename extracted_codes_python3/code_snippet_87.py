#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cmd import Cmd
import sys
import getpass
import pprint
from gmclient import GMClient


class GMCmd(Cmd):
    prompt = "> "
    host = ""
    gmclient = GMClient()
    current_project = None
    current_milestone = None

    def do_EOF(self, params):
        ''' Exit '''
        sys.exit(0)

    def do_help(self, params):
        ''' Print help '''
        if params:
            super(GMCmd, self).do_help(params)
        else:
            names = self.get_names()
            names.sort()
            cmds = []
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd = name[3:]
                    cmds.append(cmd)
            for cmd in cmds:
                cmd_doc = getattr(self, "do_"+cmd).__doc__
                print "%s - %s" % (cmd, cmd_doc.split("\n")[0])

    def do_quit(self, params):
        ''' Exit '''
        sys.exit(0)

    def do_connect(self, params):
        ''' Connect to a greenmine instance '''
        self.host = params
        username = raw_input('Username: ')
        password = getpass.getpass()
        if self.gmclient.login(self.host, username, password):
            print "Login ok"
            self.prompt = self.host+"> "
        else:
            print "Login ERROR"
            print self.gmclient.last_error

    def do_sp(self, params):
        ''' Set the current project '''
        if params:
            self.current_project = params
        else:
            self.current_project = None

    def do_gp(self, params):
        ''' Get the current project '''
        print self.current_project

    def do_sm(self, params):
        ''' Set the current milestone '''
        if params:
            self.current_milestone = params
        else:
            self.current_milestone = None

    def do_gm(self, params):
        ''' Get the current milestone '''
        print self.current_milestone

    def do_lp(self, params):
        ''' List projects '''
        for project in self.gmclient.list_projects():
            print "%d - %s - %s" % (project.get('id'), project.get('slug'), project.get('name'))

    def do_lm(self, params):
        ''' List milestones '''
        if self.current_project:
            milestones = self.gmclient.list_milestones(project=self.current_project)
        else:
            milestones = self.gmclient.list_milestones()

        for milestone in milestones:
            status = "Closed" if milestone.get('closed') else "Open"
            print "%d - %s - %s (%s)" % (milestone.get('id'), milestone.get('slug'), milestone.get('name'), status)

    def do_lus(self, params):
        ''' List user stories '''
        if self.current_milestone:
            user_stories = self.gmclient.list_user_stories(milestone=self.current_milestone)
        elif self.current_project:
            user_stories = self.gmclient.list_user_stories(project=self.current_project)
        else:
            user_stories = self.gmclient.list_user_stories()

        for user_story in user_stories:
            status = self.gmclient.resolve(user_story.get('project'), 'user_story_status', user_story.get('status'))
            print "%d - %s (%s)" % (user_story.get('id'), user_story.get('subject'), status)

    def do_lt(self, params):
        ''' List tasks '''
        if params:
            tasks = self.gmclient.list_tasks(user_story=params)
        elif self.current_milestone:
            tasks = self.gmclient.list_tasks(milestone=self.current_milestone)
        elif self.current_project:
            tasks = self.gmclient.list_tasks(project=self.current_project)
        else:
            tasks = self.gmclient.list_tasks()

        for task in tasks:
            print "%d - %s (%s)" % (task.get('id'), task.get('subject'), task.get('status'))

    def do_li(self, params):
        ''' List issues '''
        if self.current_project:
            issues = self.gmclient.list_issues(project=self.current_project)
        else:
            issues = self.gmclient.list_issues()

        for issue in issues:
            print "%d - %s (%s)" % (issue.get('id'), issue.get('subject'), issue.get('status'))

    def do_lq(self, params):
        ''' List qestions '''
        if self.current_project:
            questions = self.gmclient.list_questions(project=self.current_project)
        else:
            questions = self.gmclient.list_questions()

        for question in questions:
            print "%d - %s (%s)" % (question.get('id'), question.get('subject'), question.get('status'))

    def do_ld(self, params):
        ''' List documents '''
        if self.current_project:
            documents = self.gmclient.list_documents(project=self.current_project)
        else:
            documents = self.gmclient.list_documents()

        for document in documents:
            print "%d - %s (%s)" % (document.get('id'), document.get('subject'), document.get('status'))

    def do_vp(self, params):
        ''' View project '''
        if params:
            project = self.gmclient.get_project(params)
        elif self.current_project:
            project = self.gmclient.get_project(self.current_project)
        else:
            print "ERROR: Not valid project"
            return None
        pprint.pprint(project)

    def do_vm(self, params):
        ''' View milestone '''
        if params:
            milestone = self.gmclient.get_milestone(params)
        elif self.current_milestone:
            milestone = self.gmclient.get_milestone(self.current_milestone)
        else:
            print "ERROR: Not valid milestone"
            return None
        pprint.pprint(milestone)

    def do_vus(self, params):
        ''' View user story '''
        if params:
            user_story = self.gmclient.get_user_story(params)
            pprint.pprint(user_story)
        else:
            print "ERROR: Not valid user_story"

    def do_vt(self, params):
        ''' View task '''
        if params:
            task = self.gmclient.get_task(params)
            pprint.pprint(task)
        else:
            print "ERROR: Not valid task"

    def do_vi(self, params):
        ''' View issue '''
        if params:
            issue = self.gmclient.get_issue(params)
            pprint.pprint(issue)
        else:
            print "ERROR: Not valid issue"

    def do_vq(self, params):
        ''' View qestion '''
        if params:
            question = self.gmclient.get_question(params)
            pprint.pprint(question)
        else:
            print "ERROR: Not valid question"

    def do_vd(self, params):
        ''' View document '''
        if params:
            document = self.gmclient.get_document(params)
            pprint.pprint(document)
        else:
            print "ERROR: Not valid document"

if __name__ == '__main__':
    gmcmd = GMCmd()
    gmcmd.cmdloop()
