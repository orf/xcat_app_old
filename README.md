XCat example application
========================

This is a self-contained example application that requires [Jython](http://jython.org/) to run. Download and install 
Jython and then execute `jython example_site.py`. This will launch a webserver that listens on port 8080 and serves
up an exploitable application for you to run XCat against. The examples in the documentation all run against this 
application, so copy them to see XCat in action.

**Warning:** Don't use `apt` or `yum` to install Jython, it will be very out of date. Download the installer from 
[http://www.jython.org/downloads.html](http://www.jython.org/downloads.html) and install that.