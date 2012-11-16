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
Any device that can issue an HTTP request can get data from an Artcast server.

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
on-demand to clients.  Thus, an Artcast source can be written using virtually any language or
library that supports standard networking protocols.

Using JSON, sources can generate data of arbitrary complexity, although Artcasting favors
simplicity - you will want your data source to work well with a wide variety of devices,
including microcontrollers with minimal compute resources.

Sources may generate at any time interval that is appropriate, from seconds to days.

To make them as easy as possible to write, we include a Python module with which many
sources can be written in a few lines of code.

Server
------

The Artcast server is an HTTP server written in Python using the Tornado web framework.


Clients
-------