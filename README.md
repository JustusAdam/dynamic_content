[![Build Status](https://travis-ci.org/JustusAdam/dynamic_content.svg?branch=master)](https://travis-ci.org/JustusAdam/dynamic_content)

dynamic\_content
====

Content Management System for web application.

The goal is to create a fast and easily expandable, modular CMS for every use imaginable. When finished and polished the core should be usable with only very few modules to allow custom application as well as provide a good amount of common functionality in the core modules to make getting started quick and easy.

Currently there is no documentation and few comments and docstrings and it is by no means feature complete. Pull requests, contributions and feedback is very much welcome.

100% Python 3

## Requirements

* Database
    * Mysql/MariaDB database, tested for >= v. 5.5
    * or SQLite
    * or PostgreSQL (untested, no example config)
* Libraries
    * Python > v 3.4 http://python.org + python stdlib
    * peewee orm
    * MySQL Connector/Python library for database connection (only if using mysql)
    * PostgreSQL driver??
    

## Roadmap


* Finish basic features
    * common elements (menus/blocks) &#x2713;
    * text content &#x2713;
    * authentication &#x2713;
    * authorization &#x2713;
    * file access &#x2713;
    * theme based styling &#x2713;
    * configuration and editing via web interface &#x2718; (partially done) 
    * module based handling of editing and content &#x2713; (for all currently available content types)

* Extensibility
    * Added several decorators to allow easy use of core functionality
    * Added dynamic path mapping allow for easy addition of custom controllers    

* MISC Features
    * Special handling for other requests like traceroute etc. &#x2718;

* SQLite integration &#x2713;
