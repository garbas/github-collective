Introduction
============

`Github organization`_ are great way for organization to manage their git
repositories. This tool will let you automate tedious tasks of creating teams,
granting permission and creating repositories.

Approach that ``github-collective`` tool takes is that you edit central
configuration (for now only ini-like file) from where configuration is read and
updated respectivly.

Initially purposo of this scrip is to manage Plone's collective organisation on
github: https://collective.github.com


.. contents


How to install
==============

:Tested with: `Python2.6`_
:Dependencies: `argparse`_, `requests`_

::

    % pip install github-collective
    (or)
    % easy_install github-collective


Usage
=====

When ``github-collective`` is installed it should create executable with same
name.

::

    % bin/github-collective --help
    usage: github-collective [-h] -c CONFIG [-M MAILER] [-C CACHE] -o GITHUB_ORG
                             -u GITHUB_USERNAME -P GITHUB_PASSWORD [-v] [-p]
    
    This tool will let you automate tedious tasks of creating teams granting
    permission and creating repositories.
    
    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            path to configuration file (could also be remote
                            location). eg.
                            http://collective.github.com/permissions.cfg (default:
                            None)
      -M MAILER, --mailer MAILER
                            TODO (default: None)
      -C CACHE, --cache CACHE
                            path to file where to cache results from github.
                            (default: None)
      -o GITHUB_ORG, --github-org GITHUB_ORG
                            github organisation. (default: None)
      -u GITHUB_USERNAME, --github-username GITHUB_USERNAME
                            github account username. (default: None)
      -P GITHUB_PASSWORD, --github-password GITHUB_PASSWORD
                            github account password. (default: None)
      -v, --verbose
      -p, --pretend


Example of configuration stored locally
---------------------------------------

::

    % bin/github-collective \
        -c example.cfg \ # path to configuration file
        -o vim-addons \  # organization that we are 
        -u garbas \      # account that has management right for organization
        -P PASSWORD      # account password

Example of configuration stored on github
-----------------------------------------

::

    % bin/github-collective \
        -c https://raw.github.com/garbas/github-collective/master/example.cfg \
                         # url to configuration file
        -o collective \  # organization that we are 
        -u garbas \      # account that has management right for organization
        -P PASSWORD      # account password

Example of cached configuration
-------------------------------

::

    % bin/github-collective \
        -c https://raw.github.com/garbas/github-collective/master/example.cfg \
                         # url to configuration file
        -C .cache        # file where store and read cached results from github
        -o collective \  # organization that we are 
        -u garbas \      # account that has management right for organization
        -P PASSWORD      # account password


Todo
====

 - Send emails to owners about removing repos
 - better logging mechanism (eg. logbook)


Credits
=======

:Author: `Rok Garbas`_


Changelog
=========

0.1.1 - 2011-07-02
------------------

 - and we have first bugfix relese, after refractoring and merging
   `enable-cache` branch.
   [garbas]


0.1 - 2011-07-02
----------------

 - initial release
   [garbas]


.. _`Github organization`: https://github.com/blog/674-introducing-organizations
.. _`Python2.6`: http://www.python.org/download/releases/2.6/
.. _`argparse`: http://pypi.python.org/pypi/argparse
.. _`requests`: http://python-requests.org
.. _`Rok Garbas`: http://www.garbas.si
