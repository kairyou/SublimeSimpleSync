# SimpleSync

A basic Sublime Text 3 plugin that listens to `save` event and [r]sync the file to remote automatically.

## Installation

Clone this project into `Packages` folder:

```bash
cd [...]/Sublime Text 3/Data/Packages
git clone https://github.com/ushuz/SimpleSync.git
```

## Settings

Preferences > Package Settings > SimpleSync > Settings - User

Sample settings:

``` javascript
{
  "local": "/Users/user/projects",
  "remote": "/Users/user/projects",
  "init": "~/.bash_profile",        // Shell initialization file like `.bash_profile` or `.bashrc`
  "command": "rsync -avz",          // SimpleSync will use "[LOCAL_FILE_PATH] [REMOTE_FILE_PATH]" as arguments
  "timeout": 10,                    // Command execution timeout
}
```

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
