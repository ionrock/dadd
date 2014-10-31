===
Dad
===

Dad administers daemons!

Dad is a different kind of process manager. There are many great tools
like supervisord and daemontools for managing long running
processes. These tools can be configured to add and remove processes
as you need to scale. Dad does something different.

Here is what dad does:

 1. Start a process on a host in a temporary directory
 2. Daemonize the process
 3. On completion of the process, the temporary directory is cleaned
    up
 4. If something failed, dad notifies and records the logs

That is it!

Why Dad?
========

Many distributed computing platforms rely on each worker being
released with the code that will be run by the worker. `Celery
<http://www.celeryproject.org/>`_ is a good example of this
paradigm. The problem with this style is that it is really easy to
interrupt your workers with new releases. Dad starts the process and
immediately daemonizes it so that if a dad worker gets restarted, the
work currently being done is not effected.

Dad also makes each process reasonably atomic. It makes no assumptions
on the host other than having python installed and virtualenv. When a
process is started files can be downloaded and Python dependencies
installed in order to run some code.

Dad is not meant to automatically scale a systems or provide stats on
processes. It is meant to *run* a process as a daemon. It is the
responsibility of the process to integrate with other systems. Dad
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
    "python_deps": [
      "mypackage"
    ]
  }

When you want to run a process, you POST the spec to the dad master
server. It will find a host to run it on and send it along to the
worker. The worker will then set up a temp directory and allow a `dad
run` process download any files, install a virtualenv along with the
`python_deps` and run the command.


Dad Processes
=============

Dad comes with a command line tool that starts the different dad
processes.

Dad Master
----------

Running `dad master` will start the master server. This maintains the
list of processes and hosts. When you try to start a process it will
try to find a host. If a host is not found, that host will be removed
from the lists of hosts.


Dad Worker
----------

Run `dad worker` starts up a worker process. The if a master is
defined in the config or environment it will register itself so that
it can start accepting jobs from the master. This registration happens
periodically like a heartbeat in order to keep the workers in sync
with the master.


Dad Runner
----------

The `dad run` command runs a process as a deamon and does the build
process prior to running the command. If the master is specified in
the config and the spec contains a process ID on the master, it will
notify the master of its state as well as upload its log on failure.


* Free software: BSD license
..
   * Documentation: https://dad.readthedocs.org.
