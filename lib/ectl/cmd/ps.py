from __future__ import print_function
import multiprocessing
import os
import hashlib
import argparse
import llnl.util.tty as tty
import ectl
import ectl.cmd
from ectl import pathutil,rundeck,rundir,xhash
from ectl.rundeck import legacy
import re
from ectl import iso8601
import StringIO
import sys
import shutil
from ectl import iso8601
import datetime
import ectl.rundir
import signal
import subprocess

description = 'Reports on the status of a run.'

def setup_parser(subparser):
    subparser.add_argument('runs', nargs='*',
        help='Directory of run to give execution command')
    subparser.add_argument('-r', '--recursive', action='store_true', dest='recursive', default=False,
        help='Recursively descend directories')


def walk_rundirs(top, doruns):
    status = ectl.rundir.Status(top)
    if status.status == ectl.rundir.NONE:
        for sub in os.listdir(top):
            subdir = os.path.join(top, sub)
            if os.path.isdir(subdir):
                walk_rundirs(subdir, doruns)
    else:
        doruns.append((top,status))


## This require netCDF libraries in Python; but we want to be using
## a simple System python.
#caldateRE = re.compile(r'(\d+)/(\d+)/(\d+)\s+hr\s+(\d+).(\d+)')
#def get_caldate(fort_nc):
#    """Gets the current timestamp from a fort.1.nc or fort.2.nc file."""
#    with netCDF4.Dataset(fort_nc) as nc:
#        caldate = nc.variables['itime'].caldate
#    match = caldateRE.match(caldate)
#    return datetime.datetime(match.group(3), match.group(1), match.group(2), match.group(4), match.group(5))

caldateRE = re.compile(r'(\d+)/(\d+)/(\d+)\s+hr\s+(\d+).(\d+)')
def get_caldate(fort_nc):
    cmd = ['ncdump', '-h', fort_nc]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in proc.stdout:
        match = caldateRE.search(line)
        if match is not None:
            return datetime.datetime(int(match.group(3)), int(match.group(1)), int(match.group(2)), int(match.group(4)), int(match.group(5)))
    return None


def ps(parser, args, unknown_args):
    if len(unknown_args) > 0:
        raise ValueError('Unkown arguments: %s' % unknown_args)

    if len(args.runs) == 0:
        runs = [os.path.abspath('.')]
    else:
        runs = [os.path.abspath(run) for run in args.runs]

    recursive = args.recursive
    if (not recursive) and (len(runs) == 1):
        # Auto-recurse if a single given dir is not a run dir
        status = ectl.rundir.Status(runs[0])
        if status.status == ectl.rundir.NONE:
            recursive = True

    # ------- Get list of runs to do
    if recursive:
        doruns = list()
        for top_run in runs:
            walk_rundirs(top_run, doruns)
    else:
        doruns = [(run, ectl.rundir.Status(run)) for run in runs]

    for run,status in doruns:
        if (status.status == ectl.rundir.NONE):
            sys.stderr.write('Error: No valid run in directory %s\n' % run)
            sys.exit(-1)

        # Top-line status
        print('============================ {}'.format(os.path.split(run)[1]))
        print('status:  {}'.format(status.sstatus))

        paths = rundir.FollowLinks(run)

        # Current time
        try:
            with open(os.path.join(paths.run, 'timestep.txt')) as fin:
                sys.stdout.write(next(fin))
        except IOError as err:
            pass

        # Time in fort.1.nc and fort.2.nc
        dates = [ \
            (get_caldate(os.path.join(paths.run, 'fort.1.nc')), 'fort.1.nc'),
            (get_caldate(os.path.join(paths.run, 'fort.2.nc')), 'fort.2.nc')]
        dates = [x for x in dates if x[0] is not None]
        dates.sort()
        for dt,fname in dates:
            if dt is not None:
                print('{}: {}'.format(fname, dt))

        # Run configuration
        paths.dump()

        # Launch.txt
        if status.launch_list is not None:
            for key,val in status.launch_list:
                print('{} = {}'.format(key, val))


        # Do launcher-specific stuff to look at the actual processes running.
        launcher = status.new_launcher()
        if launcher is not None:
            launcher.ps(sys.stdout)
