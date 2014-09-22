# SimpleSync

Simple ST3 plugin that sync files to remotes. Sync gets done by `pscp.exe`, SSH key authentication (Recommended) and password authentication are supported.

## Installation

Just clone this project into your ST Packages folder:

``` bash
cd [...]/Sublime Text 3/Data/Packages
git clone https://github.com/ushuz/SimpleSync.git
```

## Settings

Preferences > Package Settings > SimpleSync > Settings - User

Sample settings:

``` javascript
{
  "config": {
    "autoSync": false,
    "debug": false,
    "timeout": 10
  },
  "rules": [
    {
      "type": "ssh",
      "host": "domain or ip",
      "port": "22",
      "username": "userName",
      "password": "passWord",
      "local" : "/Users/user/projects",
      "remote" : "/home/user/projects"
    },
    {
      "type" : "local",
      "local" : "C:\\Users\\user\\projects",
      "remote" : "D:\\Dropbox\\projects"
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
* [ushuz](https://github.com/ushuz)

## License

Copyright (c) 2009-2012 Tan Nhu

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
