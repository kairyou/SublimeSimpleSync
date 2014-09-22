# -*- coding: utf-8 -*-

import os
import platform
import sublime
import sublime_plugin
import subprocess
import threading
import zipfile


# Caches
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = 'SimpleSync'
PACKAGE_SETTINGS = PACKAGE_NAME + '.sublime-settings'
OS = platform.system()


class SyncCommand(object):

    def get_settings(self):
        return sublime.load_settings(PACKAGE_SETTINGS)

    # Get file path
    def get_path(self):
        if self.window.active_view():
            return self.window.active_view().file_name()
        else:
            # sublime.error_message(PACKAGE_NAME + ': No file_name')
            self.syncPastePath()
            return False

    # Get sync item(s) for a file
    def get_sync_item(self, local_file):
        ret = []
        # print(local_file, self.rules)
        for item in self.rules:
            # print(local_file.startswith(item['local']), local_file, item['local'])
            if local_file.startswith(item['local']):
                ret += [item]
        return [item for item in self.rules if local_file.startswith(item["local"])]

    # Support multiple rules
    def sync_file(self, local_file):
        items = self.get_sync_item(local_file)
        for item in items:
            relPath = local_file.replace(item['local'], '')
            remote_file = item['remote'] + '/' + relPath
            password = item.get("password", "")
            ppk = item.get("private_key", "")
            SCPCopy(item['host'], item['username'], password, local_file,
                    remote_file, port=item['port'], relPath=relPath, private_key=ppk).start()


# { "keys": ["alt+s"], "command": "simple_sync"},
class SimpleSyncCommand(sublime_plugin.WindowCommand, SyncCommand):
    def run(self):
        settings = self.get_settings()
        self.rules = settings.get('rules')

        # Save current file
        self.window.run_command('save')

        local_file = self.get_path()
        if local_file is not False:
            self.sync_file(local_file)


# auto run, sublime_plugin.EventListener
class SimpleSync(sublime_plugin.EventListener, SyncCommand):
    # on save
    def on_post_save(self, view):
        settings = self.get_settings()
        # print('********', settings)

        config = settings.get('config', [])
        auto = config.get("auto", False)
        local_file = view.file_name()
        # print('********', local_file)

        if auto:
            self.rules = settings.get('rules')
            self.sync_file(local_file)


# command = Command("echo 'Process started'; sleep 2; echo 'Process finished'")
# command.run(timeout=3)
class Command(object):
    def __init__(self, cmd, debug=False, expect_cmd=None):
        self.cmd = cmd
        self.expect_cmd = expect_cmd
        self.process = None
        self.msg = None
        self.debug = debug

    def run(self, timeout=10, shell=True):
        def target():
            if self.debug: print('Thread started')
            cmd = self.expect_cmd if self.expect_cmd else self.cmd
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell)
            # self.process = subprocess.Popen(cmd, shell=shell)
            # retcode = subprocess.call(args)
            # if retcode != 0:#sync failed
            # else: #sync failed
            (stdout, stderr) = self.process.communicate()
            if self.debug: print('Thread finished')
            print('%s:' % PACKAGE_NAME, stdout, stderr)
            #self.process.stdout.read().decode('utf-8')
            self.msg = stdout.decode('utf-8')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            if self.debug: print ('Terminating process')
            print('%s:' % PACKAGE_NAME, 'Timedout')
            self.process.terminate() # kill proc
            thread.join()
        # print (self.process.returncode)
    def store_key(self, shell=True):
        ret = True;
        if OS != 'Windows':
            self.cmd = self.cmd.replace('"','\\"')
        if OS == 'Windows':
            args = [self.cmd]
        elif OS == 'Darwin':
            args = [
                'osascript -e \'tell app "Terminal" to do script "%s"\'' % (self.cmd),
                'open -W -a Terminal'
            ]
        else:
            args = [
                # 'gnome-terminal -x "%s"' % (self.cmd)
                'gnome-terminal --tab -e "%s"' % (self.cmd)
            ]
        # print('OS:', OS, 'cmd:', ';'.join(args))
        r = subprocess.call(';'.join(args), shell=shell)
        if r != 0:
            ret = False
        return ret


# SCPCopy does actual copying using threading to avoid UI blocking
class SCPCopy(threading.Thread, SyncCommand):
    def __init__(self, host, username, password, local_file, remote_file, port=22, relPath="", private_key=""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.local_file = local_file
        self.remote_file = remote_file
        self.relPath = relPath
        # print('relative path:', relPath)
        self.private_key = private_key

        settings = self.get_settings()
        config = settings.get('config')
        self.debug = config['debug'] if 'debug' in config else False
        self.timeout = config['timeout'] if 'timeout' in config else 10

        threading.Thread.__init__(self)

    def run(self):
        packageDir = os.path.join(sublime.packages_path(), PACKAGE_NAME)
        # for windows
        self.remote_file = self.remote_file.replace('\\', '/').replace('//', '/')
        remote = self.username + '@' + self.host + ':' + self.remote_file

        # print(PACKAGE_NAME , self.local_file, ' -> ', self.remote_file)

        pw = []
        ext = ['-r', '-C', '-P', str(self.port), '\"%s\"' % (self.local_file), '\"%s\"' % (remote)]
        shell = True

        if OS == 'Windows':
            scp = '\"%s\"' % (os.path.join(packageDir, 'pscp.exe'))
            args = [scp]
            # args = [scp, "-v"] # show message

            if self.private_key:
                k = ["-i", self.private_key]
                args.extend(k)

            shell = False
        else:
            args = ['scp']

        args.extend(ext)
        run_cmd = ' '.join(args)
        print(PACKAGE_NAME + ': ' + run_cmd)

        expect_cmd = None
        if OS != 'Windows' and self.password: # use password, ignore authorized_keys
            # ~/.ssh/known_hosts
            expect_cmd = r'''
            expect -c "
            set timeout {timeout};
            spawn {cmd};
            expect *password* {{ send \"{password}\r\" }};
            expect "100%"
            expect eof"
            '''.format(cmd=run_cmd, password=self.password, timeout=self.timeout)
            # print(expect)

        self.i = 0
        self.done = False
        self.success = False
        self.operand = 1

        def show_loading():
            size = 8
            before = self.i % size
            after = (size - 1) - before

            if not self.done:
                sublime.status_message('%s [%s=%s]' % (PACKAGE_NAME, ' ' * before, ' ' * after))
                sublime.set_timeout(show_loading, 100)
                if not before:
                    self.operand = 1
                if not after:
                    self.operand = -1
                self.i += self.operand
            else:
                msg = 'Completed!' if self.success else 'Sync failed!'
                sublime.status_message('%s: %s' % (PACKAGE_NAME, msg))
        show_loading()

        def sync_folder():
            self.local_file = os.path.dirname(self.local_file)
            self.remote_file = os.path.dirname(os.path.dirname(self.remote_file))
            # print(self.local_file, ',', self.remote_file)
            SCPCopy(self.host, self.username, self.password, self.local_file,
                    self.remote_file, self.port,
                    private_key=self.private_key).start()

        def show_msg(msg):
            find_msg = msg.lower()
            if find_msg.find('No such file or directory'.lower()) != -1:
                if sublime.ok_cancel_dialog('No such file or directory\n' + self.relPath + '\n' + '* Do you want to sync the parent folder?'):
                    sync_folder()
            elif find_msg.find('continue connecting'.lower()) != -1 or find_msg.find('Store key in cache'.lower()) != -1:
                msg = 'Please run this command once: \n'
                msg += run_cmd + '\n'
                msg += '*** Also, you can copy this command via "Console"(ctrl+` shortcut).'
                if not command.store_key(shell=shell):
                    self.success = False
                    sublime.message_dialog(msg)
            elif find_msg.find('Host key verification failed'.lower()) != -1:
                msg = 'Please generate SSH public-key and run: \n'
                msg += 'ssh -p ' + self.port + ' ' + self.username + '@' + self.host + " 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys' < ~/.ssh/id_rsa.pub \n"
                sublime.message_dialog(msg)
            elif find_msg.find('Permission denied (publickey,password)'.lower()) != -1: # authorized faild
                msg = 'Scp auth faild. Please check your sshd_config, and enable AuthorizedKeysFile!'
                sublime.message_dialog(msg)
            elif find_msg.find('100%') != -1:
                self.success = True
            elif find_msg.find('s password:') != -1:
                msg = 'Please enlarge the ["config"]["timeout"] in %s settings (Default: 10)' % (PACKAGE_NAME)
                sublime.message_dialog(msg)
            else:
                if msg:
                    sublime.message_dialog(msg)
                else:
                    self.success = False
        try:
            command = Command(run_cmd, debug=self.debug, expect_cmd=expect_cmd)
            command.run(timeout=self.timeout, shell=shell)
            self.done = True
            if self.debug:
                print('msg:', command.msg, 'returncode:', command.process.returncode)
            show_msg(command.msg)
        except Exception as exception:
            # Alert "SimpleSync: No file_name", if the file size is zero.
            # print(exception);
            sublime.error_message(PACKAGE_NAME + ': ' + str(exception))
