# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
import threading

import sublime
import sublime_plugin


PACKAGE_NAME = "SimpleSync"
PACKAGE_SETTINGS = PACKAGE_NAME + ".sublime-settings"


class SyncCommand(object):

    def sync_paste_path(self):
        file_path = ''
        def on_done(file_path):
            # print(file_path)
            if not file_path: return
            self.sync_file(file_path)
        self.window.show_input_panel('[%s] Copy and paste local file path :' % (PACKAGE_NAME), file_path, on_done, None, None)


class SimpleSyncCommand(sublime_plugin.EventListener):
    @property
    def settings(self):
        return sublime.load_settings(PACKAGE_SETTINGS)

    def on_post_save_async(self, view):
        if not view:
            return

        local = self.settings.get("local")
        remote = self.settings.get("remote")

        local_path = view.file_name()
        if not local_path or not local_path.startswith(local):
            return
        remote_path = remote + local_path.replace(local, "")

        path = self.settings.get("path", "")
        path = ":".join((os.path.expanduser(path), os.environ.get("PATH")))
        print("{}: PATH".format(PACKAGE_NAME), path)

        timeout = self.settings.get("timeout", 10)

        command = self.settings.get("command")
        cmd = command.format(local_path, remote_path)
        print("{}: Execute".format(PACKAGE_NAME), cmd)

        Command(cmd).run(timeout, env=dict(PATH=path))


class Command(object):
    def __init__(self, cmd):
        self.cmd = shlex.split(cmd)
        self.process = None

    def run(self, timeout=10, env=None):
        def target():
            self.process = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=env)
            stdout, stderr = self.process.communicate()
            print('%s:' % PACKAGE_NAME, stdout)

        thread = threading.Thread(target=target)
        thread.start()
        ThreadProgress(thread, PACKAGE_NAME, "%s Completed" % PACKAGE_NAME)

        thread.join(timeout)
        if thread.is_alive():
            print('%s:' % PACKAGE_NAME, 'Timedout')
            self.process.terminate() # kill proc
            self.process.kill()
            thread.join()

        def show_msg(msg):
            find_msg = msg.lower()
            if find_msg.find('100%') != -1:
                self.success = True
            else:
                if msg:
                    sublime.message_dialog(msg)
                else:
                    self.success = False


class ThreadProgress(object):
    """
    Animates an indicator, [=   ], in the status area while a thread runs

    :param thread:
        The thread to track for activity

    :param message:
        The message to display next to the activity indicator

    :param success_message:
        The message to display once the thread is complete
    """

    def __init__(self, thread, message, success_message):
        self.thread = thread
        self.message = message
        self.success_message = success_message
        self.addend = 1
        self.size = 8
        sublime.set_timeout(lambda: self.run(0), 100)

    def run(self, i):
        if not self.thread.is_alive():
            if hasattr(self.thread, "result") and not self.thread.result:
                sublime.status_message("")
                return
            sublime.status_message(self.success_message)
            return

        before = i % self.size
        after = (self.size - 1) - before

        sublime.status_message("%s [%s=%s]" % \
            (self.message, " " * before, " " * after))

        if not after:
            self.addend = -1
        if not before:
            self.addend = 1
        i += self.addend

        sublime.set_timeout(lambda: self.run(i), 100)
