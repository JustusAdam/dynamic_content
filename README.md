[![Build Status](https://travis-ci.org/JustusAdam/dynamic_content.svg?branch=master)](https://travis-ci.org/JustusAdam/dynamic_content)

# dynamic_content

Content Management System for web application.

The goal is to create a fast and easily expandable, modular CMS for every use imaginable. When finished and polished the core should be usable with only very few modules to allow custom application as well as provide a good amount of common functionality in the core modules to make getting started quick and easy.

It is by no means feature complete. Pull requests, contributions and feedback are very much welcome.

100% Python 3

## Documentation

[readthedocs.org](https://dynamic-content.readthedocs.org)


## Requirements

* Database
  * SQLite, in memory for testing or persistent (included in python stdlib)
  * Mysql/MariaDB database, tested for >= v. 5.5
  * PostgreSQL (untested, no example config)
* Libraries
  * Python > v 3.4 http://python.org + python stdlib
  * peewee orm
  * MySQL Connector/Python library for database connection (only if using mysql)
  * PostgreSQL driver??

## Installation

1. Clone the repository  
`git clone https://github.com/JustusAdam/dynamic_content.git`  
* Navigate to the root folder (should be `dynamic_content`)
* Start the application by either
  * Invoking the python interpreter  
  `python3 dyc/application/main.py`
  You can specify the `--host` and `--port` (default 'localhost:9012') as well as the `--runlevel` (testing, debug, production)  
  Full information on the supported command line options can be found by calling the script with `-h` or `--help`
  * Starting the shellscript  
  `./start.sh`
* Open the webpage `choosen_host:choosen_port` with the browser of your choosing, the default being `localhost:9012`

You can look at and manipulate the settings at `dyc/includes/setting.py`


## Roadmap


* **Finish basic features**
    * common elements (menus/blocks) &#x2713;
    * text content &#x2713;
    * authentication &#x2713;
    * authorization &#x2713;
    * file access &#x2713;
    * theme based styling &#x2713;
    * configuration and editing via web interface &#x2718; (partially done)
    * module based handling of editing and content &#x2713; (for all currently available content types)
* **Extensibility**
    * Added several decorators to allow easy use of core functionality
    * Added dynamic path mapping allow for easy addition of custom controllers
* **MISC Features**
    * Special handling for other requests like traceroute etc. &#x2718;
* **SQLite integration** &#x2713;
