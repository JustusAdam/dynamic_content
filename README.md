\_JAIDE
====

Content Management System for web application.

The goal is to create a fast and easily expandable, modular CMS for every use imaginable. When finished and polished the core should be usable without any core modules to allow custom application as well as a good amount of common functionality in the core modules to make getting started quick and easy.

Currently there is no documentation and few comments and docstrings and it is by no means feature complete. Pull requests, contributions and feedback is very much welcome.

100% Python ... not anymore. There's quite a bit of json in there and I plan to integrate a hash function for hashing user passwords written in C and yes, I know writing your own crypto is bad, but I want to and I might use a library if I find one I like.

Requirements
---
* Mysql/MariaDB database, tested for >= v. 5.5 (sqlite integration planned)
* PyMySQL library for database connection https://github.com/PyMySQL/PyMySQL
* Python > v 3.4 http://python.org

Roadmap
---
* Finish basic features
    * common elements (menus/blocks) &#x2713;
    * text content &#x2713;
    * authentication
    * file access &#x2713;
    * theme based styling &#x2713;
    * configuration and editing via web interface 
    * module based handling of editing and content &#x2713; (for all currently available content types)
* SQLite integration