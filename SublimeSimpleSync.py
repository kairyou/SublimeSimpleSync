#
# Sublime Text 2/3 SimpleSync plugin
#
# based on https://github.com/tnhu/SimpleSync
#

import os
# import sys
import platform
import subprocess
import threading
# import re
import sublime
import sublime_plugin
import zipfile
# print(os.path.join(sublime.packages_path(), 'Default'))

# Caches
#__name__ # ST3 bug with __name__
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = 'SublimeSimpleSync'
PACKAGE_SETTINGS = PACKAGE_NAME + '.sublime-settings'
OS = platform.system()
# print('*********', os.name, sys.platform, OS)
IS_GTE_ST3 = int(sublime.version()[0]) >= 3
VERSION = '20140721' #version


class syncCommand():

    # get settings
    def getSetting(self):
        return sublime.load_settings(PACKAGE_SETTINGS)

    # Get file path
    def getPath(self):
        if self.window.active_view():
            return self.window.active_view().file_name()
        else:
            # sublime.error_message(PACKAGE_NAME + ': No file_name')
            self.syncPastePath()
            return False

    # Get sync item(s) for a file
    def getSyncItem(self, localFile):
        ret = []
        # print(localFile, self.rules)
        for item in self.rules:
            # print(localFile.startswith(item['local']), localFile, item['local'])
            if localFile.startswith(item['local']):
                ret += [item]
        return ret

    # support multiple rules
    def syncFile(self, localFile):
        syncItems = self.getSyncItem(localFile)
        # print('+++ syncCommand: ', syncItems)
        if (len(syncItems) > 0):
            for item in syncItems:
                # fix path(/)
                relPath = localFile.replace(item['local'], '')
                remoteFile = item['remote'] + '/' + relPath
                # print('********', remoteFile)
                if (item['type'] == 'ssh'):
                    password = item['password'] if 'password' in item else ''
                    ScpCopier(item['host'], item['username'], password, localFile, remoteFile, port=item['port'], relPath=relPath).start()
                elif (item['type'] == 'local'):
                    LocalCopier(localFile, remoteFile).start()

    def syncPastePath(self):
        file_path = ''
        def on_done(file_path):
            # print(file_path)
            if not file_path: return
            self.syncFile(file_path)
        self.window.show_input_panel('[%s] Copy and paste local file path :' % (PACKAGE_NAME), file_path, on_done, None, None)

# show_input_panel and paste local file path
# { "keys": ["alt+shift+s"], "command": "sublime_simple_sync_path"},
class SublimeSimpleSyncPathCommand(sublime_plugin.WindowCommand, syncCommand):
    def run(self):
        settings = self.getSetting()
        self.rules = settings.get('rules')
        self.syncPastePath()

# { "keys": ["alt+s"], "command": "sublime_simple_sync"},
class SublimeSimpleSyncCommand(sublime_plugin.WindowCommand, syncCommand):
    def run(self):
        # for x in self.window.views(): print(x.file_name())
        settings = self.getSetting()
        self.rules = settings.get('rules')
        # auto save
        self.window.run_command('save')

        localFile = self.getPath()
        # print('********', localFile)
        if localFile is not False:
            self.syncFile(localFile)


# auto run, sublime_plugin.EventListener
class SimpleSync(sublime_plugin.EventListener, syncCommand):
    # on save
    def on_post_save(self, view):
        settings = self.getSetting()
        # print('********', settings)

        config = settings.get('config', [])
        autoSycn = config['autoSync'] if 'autoSync' in config else False
        localFile = view.file_name()
        # print('********', localFile)

        if autoSycn:
            self.rules = settings.get('rules')
            self.syncFile(localFile)

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
            (stdout, stderr) = self.process.communicate()
            # print(stdout, stderr)
            if self.debug: print('Thread finished')
            #self.process.stdout.read().decode('utf-8')
            self.msg = stdout.decode('utf-8')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            if self.debug: print ('Terminating process')
            self.process.terminate() # kill proc
            thread.join()
        # print (self.process.returncode)
    def store_key(self, shell=True):
        ret = True;
        if OS != 'Windows':
            self.cmd = self.cmd.replace('"','\\"')
        # if OS == 'Windows':
        #     args = [self.cmd]
        if OS == 'Darwin':
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

# ScpCopier does actual copying using threading to avoid UI blocking
class ScpCopier(threading.Thread, syncCommand):
    def __init__(self, host, username, password, localFile, remoteFile, port=22, relPath=''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.localFile = localFile
        self.remoteFile = remoteFile
        self.relPath = relPath
        # print('relative path:', relPath)

        settings = self.getSetting()
        config = settings.get('config')
        self.debug = config['debug'] if 'debug' in config else False
        self.timeout = config['timeout'] if 'timeout' in config else 10

        threading.Thread.__init__(self)

    def run(self):
        packageDir = os.path.join(sublime.packages_path(), PACKAGE_NAME)
        # for windows
        self.remoteFile = self.remoteFile.replace('\\', '/').replace('//', '/')
        remote = self.username + '@' + self.host + ':' + self.remoteFile

        # print(PACKAGE_NAME , self.localFile, ' -> ', self.remoteFile)

        pw = []
        ext = ['-r', '-C', '-P', str(self.port), '\"%s\"' % (self.localFile), '\"%s\"' % (remote)]
        shell = True

        if OS == 'Windows':
            # cmd = os.environ['SYSTEMROOT'] + '\\System32\\cmd.exe'

            scp = '\"%s\"' % (os.path.join(packageDir, 'pscp.exe'))
            args = [scp]
                # args = [scp, "-v"] # show message

            # run with .bat
            # scp = os.path.join(packageDir, 'sync.bat')
            # args = [scp]
            # pw.extend(ext)
            # pw = ' '.join(pw)
            # args.extend([packageDir, pw])
            if self.password:
                pw = ['-pw', self.password]
            args.extend(pw)
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

        self.i = 1
        self.done = False
        self.success = False

        def show_loading():
            # print(self.i)
            if self.i % 2 == 0:
                s = 0
                e = 3
            else:
                s = 3
                e = 0
            if not self.done:
                sublime.status_message('%s [%s=%s]' % (PACKAGE_NAME, ' ' * s, ' ' * e))
                sublime.set_timeout(show_loading, 500)
                self.i += 1
            else:
                msg = 'Completed!' if self.success else 'Sync failed!'
                sublime.status_message('%s: %s' % (PACKAGE_NAME, msg))
        show_loading()
        # return
        def sync_folder():
            self.localFile = os.path.dirname(self.localFile)
            self.remoteFile = os.path.dirname(os.path.dirname(self.remoteFile))
            # print(self.localFile, ',', self.remoteFile)
            ScpCopier(self.host, self.username, self.password, self.localFile, self.remoteFile, self.port).start()

        def show_msg(msg):
            find_msg = msg.lower()
            if find_msg.find('No such file or directory'.lower()) != -1:
                if sublime.ok_cancel_dialog('No such file or directory\n' + self.relPath + '\n' + '* Do you want to sync the parent folder?'):
                    sync_folder()
            elif find_msg.find('continue connecting'.lower()) != -1:# or find_msg.find('Store key in cache'.lower()) != -1 #(remove Windows)
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
                    self.success = True
        try:
            if OS == 'Windows':
                retcode = subprocess.call(run_cmd)
                if self.debug:
                    print('returncode:', retcode)
                if retcode != 0:
                    #sync failed
                    self.success = False
                    msg = 'Please verify that your settings(username, password, host, port) is correct and try again'
                    sublime.message_dialog(msg)
                else:
                    self.success = True
                    #sync failed
            else:
                command = Command(run_cmd, debug=self.debug, expect_cmd=expect_cmd)
                command.run(timeout=self.timeout, shell=shell)
                if self.debug:
                    print('msg:', command.msg, 'returncode:', command.process.returncode)
                show_msg(command.msg)
            self.done = True

        except Exception as exception:
            # Alert "SimpleSync: No file_name", if the file size is zero.
            # print(exception);
            sublime.error_message(PACKAGE_NAME + ': ' + str(exception))

# LocalCopier does local copying using threading to avoid UI blocking
class LocalCopier(threading.Thread, syncCommand):
    def __init__(self, localFile, remoteFile):
        self.localFile = localFile
        self.remoteFile = remoteFile

        # settings = self.getSetting()
        # config = settings.get("config")
        # self.debug = config['debug'] if "debug" in config else False
        threading.Thread.__init__(self)

    def run(self):
        # print(PACKAGE_NAME, self.localFile, ' -> ', self.remoteFile)

        if OS == 'Windows':
            # args = ['copy', '/y']
            args = ['xcopy', '/y', '/s', '/h']

            # folder path
            # print(os.path.split(self.remoteFile)[0])
            # print(os.path.dirname(self.remoteFile))
            # print(re.sub(r'\\[^\\]*$', '', self.remoteFile))

            # print('*********', self.remoteFile)
            # replace C:\test/\test\ -> C:\test\test\
            self.remoteFile = self.remoteFile.replace('/\\', '\\').rstrip('/')
            # replace /path/file.ext -> /path
            self.remoteFile = os.path.dirname(self.remoteFile) + '\\'
            # print('*********', self.remoteFile)
        else:
            args = ['cp']
        args.extend([self.localFile, self.remoteFile])

        print(PACKAGE_NAME + ': ' + ' '.join(args))
        # return
        try:
            retcode = subprocess.call(' '.join(args), shell=True)
            print(retcode)
            msg = 'Completed!' if retcode == 0 else 'Sync failed!'
            sublime.status_message('%s: %s' % (PACKAGE_NAME, msg))

        except Exception as exception:
            # print(exception);
            sublime.error_message(PACKAGE_NAME + ': ' + str(exception))


def plugin_loaded():  # for ST3 >= 3016
    PACKAGES_PATH = sublime.packages_path()
    TARGET_PATH = os.path.join(PACKAGES_PATH, PACKAGE_NAME)
    # print(TARGET_PATH);
    # first run
    version_file = os.path.join(TARGET_PATH, 'version')
    # print(PACKAGE_NAME, VERSION, version_file)
    version = 0
    if os.path.isfile(version_file):
        f = open(version_file, 'r')
        version = f.read().strip() # lines = f.readlines()
        f.close()
    # print(VERSION, version, VERSION == version)
    if not os.path.isdir(TARGET_PATH) or not VERSION == version:
        # copy files
        file_list = [
            'Main.sublime-menu', 'pscp.exe',
            # 'SublimeSimpleSync.py',
            'version',
            'README.md',
            'SublimeSimpleSync.sublime-settings',
            'sync.bat'
        ]
        try:
            os.makedirs(TARGET_PATH)
            extract_zip_resource(BASE_PATH, file_list, TARGET_PATH)
        except Exception as e:
            print(e)

if not IS_GTE_ST3:
    sublime.set_timeout(plugin_loaded, 0)

def extract_zip_resource(path_to_zip, file_list, extract_dir=None):
    if extract_dir is None:
        return
    # print(extract_dir)
    if os.path.exists(path_to_zip):
        z = zipfile.ZipFile(path_to_zip, 'r')
        for f in z.namelist():
            # if f.endswith('.tmpl'):
            if f in file_list:
                # print(f)
                z.extract(f, extract_dir)
        z.close()
