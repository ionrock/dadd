====
Dadd
====

Dadd administers daemons!

Dadd is a different kind of process manager. There are many great tools
like supervisord and daemontools for managing long running
processes. These tools can be configured to add and remove processes
as you need to scale. Dadd does something different.

Here is what dadd does:

 1. Start a process on a host in a temporary directory
 2. Daemonize the process
 3. On completion of the process, the temporary directory is cleaned
    up
 4. If something failed, dadd notifies and records the logs

That is it!

Why Dadd?
=========

Many distributed computing platforms rely on each worker being
released with the code that will be run by the worker. `Celery
<http://www.celeryproject.org/>`_ is a good example of this
paradigm. The problem with this style is that it is really easy to
interrupt your workers with new releases. Dadd starts the process and
immediately daemonizes it so that if a dadd worker gets restarted, the
work currently being done is not effected.

Dadd also makes each process reasonably atomic. It makes no assumptions
on the host other than having python installed and virtualenv. When a
process is started files can be downloaded and Python dependencies
installed in order to run some code.

Dadd is not meant to automatically scale a system or provide stats on
processes. It is meant to *run* a process as a daemon. It is the
responsibility of the process to integrate with other systems. Dadd
expects the process to exit on its own.


Defining Processes
==================

Processes are defined via a spec. A spec is just some JSON that
defines a couple keys. Here is an example: ::

  {
    "cmd": "python -m mypackage"
    "download_urls": [
      "https://s3.com/mybucket/some_data.json",
    ],
    "config": {
      "db": "postgres://username:pw@dbhost:5432/mydb",
    },
    "python_deps": [
      "mypackage"
    ],
    "python_cheeseshop": "http://cheese.mydomain.net"
  }

When you want to run a process, you POST the spec to the dadd master
server. It will find a host to run it on and send it along to the
worker. The worker will then set up a temp directory and allow a `dadd
run` process download any files, install a virtualenv along with the
`python_deps` and run the command.

Any configuration provided in the spec will be written to the
temporary directory as JSON. The filename will be available to the
process in the environment via the `APP_SETTINGS_JSON` env var.

If you need to install packages from a specific cheese shop, you can
provide a `python_cheeseshop` in the spec and it will be used when
installing any Python dependencies.


Dadd Processes
==============

Dadd comes with a command line tool that starts the different dadd
processes.

Dadd Master
-----------

Running `dadd master` will start the master server. This maintains the
list of processes and hosts. When you try to start a process it will
try to find a host. If a host is not found, that host will be removed
from the lists of hosts.


Dadd Worker
-----------

Run `dadd worker` starts up a worker process. The if a master is
defined in the config or environment it will register itself so that
it can start accepting jobs from the master. This registration happens
periodically like a heartbeat in order to keep the workers in sync
with the master.


Dadd Runner
-----------

The `dadd run` command runs a process as a deamon and does the build
process prior to running the command. If the master is specified in
the config and the spec contains a process ID on the master, it will
notify the master of its state as well as upload its log on failure.


* Free software: BSD license

.. * Documentation: https://dadd.readthedocs.org.
