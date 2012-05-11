#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================



"""
Wraps the standard DVCS commands: for mercurial.

https://bitbucket.org/kevindunn/ucommentapp/src/c0b839e548b7/hgwrapper.py

"""
# Dictionary of Mercurial verbs: first list entry is the actual verb to use at
# the command line, while the second entry is a dict of error codes and their
# corresponding error messages.
hg_verbs = {'pull':   ['pull', {}],
            'update': ['update', {1: 'Unresolved files.'}],
            'merge':  ['merge', {255: 'Conflicts during merge'}],
            'clone':  ['clone', {}],
            'init':   ['init', {}],
            'add':    ['add', {}],
            'heads':  ['heads', {0: '<string>'}],
            'commit': ['commit', {1: 'Nothing changed'}],
            'push':   ['push', {}],
            'summary':['summary', {0: '<string>'}], # return stdout
            }

# Can be overridden by the module that calls this module, i.e. in ``views.py``:
#    import hgwrapper as dvcs
#    dvcs.executable = '/usr/bin/hg'
executable = '/usr/local/bin/hg'

# Path to the local repo. It must exist prior to calling any function in this
# module and must be specified by the calling module, i.e. in ``views.py``:
#    import hgwrapper as dvcs
#    dvcs.local_repo_physical_dir = '/home/myname/repos/my-document/'
local_repo_physical_dir = None

# Will be set to true during unit tests
testing = False

import re, subprocess
from sphinx.util.osutil import ensuredir

class DVCSError(Exception):
    """
    Exception class that must be used to raise any errors related to the DVCS
    operations.
    """
    pass

def _run_hg_command(command, override_dir=''):
    """
    Runs the given command, as if it were typed at the command line, in the
    appropriate directory.
    """
    verb = command[0]
    actions = hg_verbs[verb][1]
    try:
        command[0] = hg_verbs[verb][0]
        command.insert(0, executable)
        ensuredir(override_dir or local_repo_physical_dir)
        out = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=override_dir or local_repo_physical_dir)
        if testing:
            # For some strange reason, unit tests fail if we don't have
            # a small pause here.
            import time
            time.sleep(0.1)

        stderr = out.stderr.readlines()
        if stderr:
            return stderr

        if out.returncode == 0 or out.returncode is None:
            if actions.get(0, '') == '<string>':
                return out.communicate()[0]
            else:
                return out.returncode
        else:
            return out.returncode

    except OSError as err:
        if err.strerror == 'No such file or directory':
            raise DVCSError('The ``hg`` executable file was not found.')


def get_revision_info(remote=False):
    """
    Returns the unique hexadecimal string the represents the current changeset.

    If ``remote`` is True, then it will return the repo information for the
    remote repo associated with the local repo.

    If ``remote`` is a string, then it assumes it is a fully qualified
    locate to another repository (but not an unrelated repo) that can be
    accessed without authentication.
    """
    if isinstance(remote, bool):
        if remote is True:
            output = _run_hg_command(['summary', '--remote'])
        else:
            output = _run_hg_command(['summary', '-R', local_repo_physical_dir])
    elif isinstance(remote, basestring):
        if remote.startswith('file://'):
            remote = remote.partition('file://')[2]
        output = _run_hg_command(['summary'], override_dir=remote)

    # Used to signal that a repo does not exist yet:
    if output[0][0:5] == 'abort':
        raise(DVCSError(output[0]))
    source = output.split('\n')[0].split(':')
    return source[2].split()[0]

def init(dest):
    """
    Creates a repository in the destination directory, ``dest``.

    This function is not required in ucomment; it is only used for unit-testing.
    """
    out = _run_hg_command(['init', dest], override_dir=dest)
    if out != None and out != 0:
        raise DVCSError('Could not initialize the repository at %s' % dest)

def add(repo, *pats):
    """
    Adds one or more files to the repository, using Mercurial's syntax for
    ``hg add``.  See ``hg help patterns`` for the syntax.

    This function is not required in ucomment; it is only used for unit-testing.
    """
    command = ['add']
    command.extend(pats)
    out = _run_hg_command(command, override_dir=repo)
    if out != None and out != 0:
        raise DVCSError('Could not add one or more files to repository.')

def check_out(rev='tip'):
    """
    Operates on the local repository to update (check out) the revision
    to the given revision number.  The default revision is the `tip`.

    Returns the revision info after update, so that one can verify the update
    succeeded.
    """
    # Use str(0), because 0 by itself evaluates to None in Python logical checks
    _run_hg_command(['update', '-r', str(rev)])
    return get_revision_info()

def clone_repo(source, dest):
    """ Creates a clone of the remote repository given by the ``source`` URL,
    and places it at the destination URL given by ``dest``.

    Returns the hexadecimal revision number of the destination repo.
    """
    out = _run_hg_command(['clone', source, dest])
    if out != None and out != 0:
        raise DVCSError(('Could not clone the remote repo, %s, to the required '
                         'local destination, %s.' % (source, dest)))
    return get_revision_info()

def commit(message, override_dir=''):
    """
    Commit changes to the ``repo`` repository, with the given commit ``message``
    Returns the hexadecimal revision number.
    """
    _run_hg_command(['commit', '-m', message], override_dir)
    if override_dir:
        return  # Used for unit testing: no output required
    else:
        return get_revision_info()

def commit_and_push_updates(message):
    """
    After making changes to file(s), programatically commit them to the local
    repository, with the given commit ``message``; then push changes
    back to the source repository from which the local repo was cloned.
    """
    # Update in the local repo first: can happen when, for example a comment is
    # resubmitted on the same node and the first commit has not been pushed
    # through to the remote server.
    output = _run_hg_command(['update'])
    if output is not None:
        return False

    # Then commit the changes
    _run_hg_command(['commit', '-m', message])

    # Try pushing the commit
    out = _run_hg_command(['push'])
    if out != None and out != 0:
        raise DVCSError(('Could not push changes to the source repository: '
                          'additional info = %s' % out[0].strip()))

    return get_revision_info()

def pull_update_and_merge():
    """
    Pulls, updates and merges changes from the other ``remote`` repository into
    the ``local`` repository.

    If the "pull" results on more than one head, then we will merge.
    See: http://hgbook.red-bean.com/read/a-tour-of-mercurial-merging-work.html

    After merging, it will automatically commit and leave the local repo at
    this tip revision.

    We cannot handle the case where merging fails!  In that case we will return
    a DVCSError.
    """

    # Performs the equivalent of "hg pull -u; hg merge; hg commit"

    # Pull in all changes from the remote repo and update.
    _run_hg_command(['pull', '-u'])
    # Above will return a message: "not updating, since new heads added"
    # if we require merging.

    # Anything to merge?  Are there more than one head?
    output_heads = _run_hg_command(['heads'])
    num_heads = len(re.findall('changeset:   (\d)+', output_heads))

    # Merge any changes:
    if num_heads > 1:
        merge_error = _run_hg_command(['merge'])

        # Commit any changes from the merge
        if not merge_error:
            commit(('Auto commit - ucomment hgwrapper: '
                                           'updated and merged changes.'))
        else:
            raise DVCSError(('Could not automatically merge during update. '
                             'More info = %s' % merge_error[0].strip()))
