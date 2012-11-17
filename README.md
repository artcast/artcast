Overview
========
This is the Artcast server: a special-purpose web server developed by the Artcast Project 
that is dedicated to the task of delivering time varying data for use in:

* Interactive artwork
* Kinetic sculpture
* Maker projects
* School assignments
* Cool hacks
* Whatever you dream up!

Artcast is designed to deliver data in a way that is simple, efficient, and low-latency.
Any device that can issue an HTTP request can receive data from an Artcast server.

Design
======

There are three components in an Artcast system:

* Sources
* Server
* Clients

Sources
-------

An Artcast source is a program that generates time varying data for distribution by the
Artcast server.  Each datum generated by the source is a key-value pair where the key is
an arbitrary string, and the value is a JSON-encoded data structure.  These pairs are
transmitted to one-or-more Artcast servers using multicast UDP, where they are distributed
to clients.  Thus, an Artcast source can be written using virtually any language or
library that supports standard networking protocols.

Using JSON, sources can generate data of arbitrary complexity, although Artcasting favors
simplicity - you will want your data source to work well with a wide variety of devices,
including microcontrollers with minimal compute resources.

Sources may generate dadta at any time interval that is appropriate, from fractions of a
second to years.

To make them as easy as possible to write, we include a Python module with which many
sources can be written in a few lines of code.

Server
------

The Artcast server is an HTTP server written in Python using the Tornado web framework.


Clients
-------

An Artcast client is any device or program that can make an HTTP request of the server
and display / render / interpret the resulting value.  A client requests the next available
value from an Artcast source by performing an HTTP GET request
to the URL http://[server]/artcasts/[key] ... a response to the request is returned by the server as soon
as a datum that matches [key] is received from an Artcast source.  Once a client has
received the datum it can make a request for the next value.  Thus, Artcast clients use
long-polling to receive Artcast values as soon as they're available with a minimum of
latency and network traffic

As with sources, clients can be written with any language or
framework, or use existing platforms such as web browsers.

Installation
============

To install the Artcast server, you will need the following:

* Python 2.6 or greater - <http://www.python.org>
* Tornado 2.4 web server - <http://www.tornadoweb.org>
* Python-Daemon - <http://pypi.python.org/pypi/python-daemon/>

Once you've installed the required modules, preferably using the package manager for your system, you
can get the server source code and run it:

    $ git clone git://github.com/artcast/artcast.git
    $ cd artcast/server
    $ python server.py

