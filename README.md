# SublimeSimpleSync

Simple Sublime Text 2/3 plugin for SSH and local syncing, support Windows/Mac/Linux.

## Before you start

- SSH synchronization is done via scp, support SSH key authentication(Mac/Linux) and password authentication(Windows/Mac/Linux).

## Installation

### Manually

Clone this project into your ST Packages folder, for example:

``` bash
cd [...]/Sublime Text 2/Packages
git clone https://github.com/kairyou/SublimeSimpleSync.git SublimeSimpleSync
```

### Using Package Control

Search for SublimeSimpleSync in Package Control and install it.  
Note: Please update to latest version and delete `/Packages/SublimeSimpleSync/SublimeSimpleSync.py` once. (You can't use the latest version until remove this file. The latest version has remove this file).

## Settings

When you finish installing SimpleSync, its settings can be found in Preferences > Package Settings > SublimeSimpleSync Settings

Sample settings:

``` javascript
{
  "config": {
    "autoSync": false,
    "debug": false,
    "timeout": 10 //support mac/linux
  },
  "rules": [
  {
    "type": "ssh", "host": "domain or ip", "port": "22",
    "username": "userName", "password": "passWord", // support windows/Mac/linux
    "local" : "/Users/projects/projectA",
    "remote" : "/home/projectA/"
  },
  {
    "type" : "local",
    "local" : "E:\\projectFolder\\projectA",
    "remote" : "D:\\bakup\\projectA"
  }
  ]
}
```

## Add key bindings

Preferences > Key Bindings - User

    { "keys": ["alt+s"], "command": "sublime_simple_sync"},
    { "keys": ["alt+shift+s"], "command": "sublime_simple_sync_path"},

Files are saved to remote server automatically when you save them locally. In case of "local" syncing, they are copied to "remote" folder which is on the same machine.

## Contributors

* [tnhu](https://github.com/tnhu)
* [gfreezy](https://github.com/gfreezy)
* [kairyou](https://github.com/kairyou)
* [Jan van Valburg](https://github.com/jan11011977)

* [中文文档](http://www.fantxi.com/blog/archives/sublime-simple-sync/)

## License

Copyright (c) 2009-2012 Tan Nhu

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
