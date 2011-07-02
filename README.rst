Introduction
============

`Github organization`_ are great way for organization to manage their git
repositories. This tool will let you automate tedious tasks of creating teams,
granting permission and creating repositories.

Approach that ``github-collective`` tool takes is that you edit central
configuration (for now only ini-like file) from where configuration is read and
updated respectivly.


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


Example of configuration stored locally
---------------------------------------

::

    % bin/github-collective \
        -c example.cfg \  # path to configuration file
        -o collective \  # organization that we are 
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

Credits
=======

:Author: `Rok Garbas`_


Changelog
=========

0.1 - 2011-07-02
----------------

 - initial release



.. _`Github organization`: https://github.com/blog/674-introducing-organizations
.. _`Python2.6`: http://www.python.org/download/releases/2.6/
.. _`argparse`: http://pypi.python.org/pypi/argparse
.. _`requests`: http://python-requests.org
.. _`Rok Garbas`: http://www.garbas.si
