# -*- coding: utf-8 -*-

from fabric.api import local, settings, abort, run, cd, env, prefix, execute, task, lcd
from fabric.decorators import roles, parallel, serial
from fabric.utils import abort, warn
from functools import wraps
import os, sys, posixpath
from collections import namedtuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # The base dir of the project.

################################################################################
# How to use this file:
#
# All local commands start with `local_`. The other commands are remote.
#
# For running a local command, set the PHACEOLOGY_SERVER_CONFIG_DIR environment
# variable to point to a directory with an `phaceology_local_settings.py` file
# setting all the required environment variables in `os.environ`
#
# The main command to run a remote deploy is 'fab deploy'.
#
# For all remote deployment, you need the credentials to be able to SSH into the
# remote machines. Check online for documentation for configuring SSH to put the
# right keys in the right places.
#
################################################################################

env.setdefault('tests', 'lp')

env.roledefs = {
    'head': ['phaceology.looplingo.com'],
    'backup': [],
    }

################################################################################
## Configuration

PathList = namedtuple('DirList', 'code server_config')

PATHS = PathList(
    code = '/home/ubuntu/src/phaceology',
    server_config = 'FILL IN',
)

STAGE_PATHS = PathList(
    code = '/home/phaceology/src/phaceology',
    server_config = 'FILL IN',
)

LOCAL_PATHS = PathList(
    code = os.path.dirname(__file__),
    server_config = os.environ.get('PHACEOLOGY_SERVER_CONFIG_DIR', os.path.join(BASE_DIR, 'local_settings', 'development')), # Path to a directory with phaceology_local_settings.py files.
)


env.user = 'phaceology'

################################################################################
## More helper functions

def _islocal():
    '''Tells if the currently running script is tagged as being local.'''
    return getattr(env, 'islocal', False)

def _run(*args, **kwargs):
    '''Call either run or local, depending on if we're running locally.'''
    if _islocal():
        return local(*args, **kwargs)
    return run(*args, **kwargs)

def _cd(*args, **kwargs):
    '''Call either cd or lcd, depending on if we're running locally.'''
    if _islocal():
        return lcd(*args, **kwargs)
    return cd(*args, **kwargs)

def _get_paths():
    '''Get either the local paths or the remote paths.'''
    if _islocal():
        return LOCAL_PATHS
    else:
        return env.paths

def _env():
    'Context manager to set environment variables from the server-config.'
    return prefix("export DJANGO_SETTINGS_MODULE='phaceology.settings'")
    #return prefix("export PHACEOLOGY_SERVER_CONFIG='%s' DJANGO_SETTINGS_MODULE='phaceology.settings'" % _get_paths().server_config)

def _code_dir():
    'Context manager to cd to the code directory.'
    return _cd(_get_paths().code)

def _frontend_code_dir():
    'Context manager to cd to the front end code directory.'
    return _cd(posixpath.join(_get_paths().code, 'frontend'))

def _server_config_dir():
    'Context manager to cd to the server config directory.'
    return _cd(_get_paths().server_config)

def _venv():
    'Context manager to enable the virtualenv.'
    return prefix('. %s' % os.path.join(_get_paths().code, 'env/bin/activate'))

def _localtask(fn):
    'Decorator to mark the task as running locally.'
    @wraps(fn)
    def _local_wrapper(*args, **kwargs):
        # This breaks if a local task calls a remote task, but you shouldn't do
        # that.
        waslocal = getattr(env, 'islocal', False)
        env.islocal = True
        ret = fn(*args, **kwargs)
        env.islocal = waslocal
        return ret
    return _local_wrapper

def _set_xterm_title(title):
    sys.stdout.write("\x1b]2;%s\x07" % title)

title_stack = []
def _show_in_titlebar(fn):
    'Decorator to show a task in the XTerm titlebar while it is running.'
    @wraps(fn)
    def show_in_titlebar_wrapper(*args, **kwargs):
        title = '** RUN: %s **' % fn.__name__
        title_stack.append(title)
        _set_xterm_title(title)
        ret = fn(*args, **kwargs)
        title_stack.pop()
        _set_xterm_title(title_stack[0] if title_stack else '** DONE: %s **' % fn.__name__)
        return ret
    return show_in_titlebar_wrapper


################################################################################
# Remote Tasks

# ES: TODO: Most of this was copied from LoopLingo, so it will all need updating for Phaceology

@task
@_show_in_titlebar
@roles('head', 'backup')
@parallel
def update_code():
    # First update the server-config
    #with _server_config_dir():
    #    run("git pull")
    # Do a git pull in the source code directory.
    with _code_dir(), _env():
        run("git pull")
    # Update the virtual environment, maybe.
    execute(update_venv)
    
@task
@_show_in_titlebar
@roles('head', 'backup')
def update_venv():
    with _code_dir(), _env():
        _run('scripts/maybe-update-venv.py')
    

@task
@_show_in_titlebar
@roles('head', 'backup')
def manage(*args):
    '''
    Run a Django command from manage.py within the appropriate environment. The
    arguments must be specified using the Fabric convention, separated by
    commas, like follows:

    fab local_manage:validate,--no-input
    '''
    execute(update_venv)
    with _code_dir(), _env(), _venv():
        _run("./manage.py %s --traceback" % ' '.join(args))
    

@task
@_show_in_titlebar
@roles('head',)
def status():
    '''
    git status ; (on head server)
    '''
    with _code_dir(), _env():
        _run('git status')

@task
@_show_in_titlebar
@roles('head', 'backup')
def venv_run(cmd):
    '''
    Run a command inside the virtualenv on all servers.
    '''
    with _code_dir(), _venv(), _env():
        _run(cmd)


@task
@_show_in_titlebar
@roles('head', 'backup')
def check_has_bower(is_local=False):
    from pkg_resources import parse_version
    from functools import partial
    dorun = partial(local, capture=True) if is_local else run
    bower_version = dorun('bower --version')
    print ('Bower version %s' % bower_version)
    if parse_version(bower_version) < parse_version('1.4.0'):
        abort('You need to have at least version 1.4.0 of bower installed. You have version %s' % bower_version)
        

@task
@_show_in_titlebar
@roles('head', 'backup')
@serial
def copy_media():
    '''
    Copy demo media files to the proper location on the server.
    '''
    with _code_dir():
        _run('mkdir -p media')
        _run('cp -avu demo_media/* media/')


@task
@_show_in_titlebar
@roles('head', 'backup')
def npm_install():
    with _frontend_code_dir(), _env():
        _run('npm install')

@task
@_show_in_titlebar
@roles('head', 'backup')
def make_settings_json():
    with _code_dir(), _env(), _venv():
        _run('./manage.py settingsjson > djangoSettings.json')

@task
@_show_in_titlebar
@roles('head', 'backup')
def webpack():
    execute(make_settings_json)
    with _frontend_code_dir(), _env():
        _run('npm run webpack')

@task
@_show_in_titlebar
@roles('head', 'backup')
def webpackwatch():
    execute(make_settings_json)
    with _frontend_code_dir(), _env():
        _run('npm run webpackwatch')


@task
@_show_in_titlebar
@roles('head')
def head_deploy(frontend=True):
    '''
    Run the deployment commands that should only be run on the head
    server.
    '''
    with _code_dir(), _venv(), _env():
        _run('./manage.py migrate --noinput --traceback')
        _run('./manage.py makeadmin --traceback')
        _run('./manage.py demodata --traceback')
        if frontend:
            execute(npm_install)
            execute(webpack)
        _run('./manage.py collectstatic -l --noinput --traceback') # ES: TODO: Make this not use the -l flag.
    
@task
@_show_in_titlebar
@roles('head', 'backup')
def celery():
    '''
    (Re)start the Celery workers.
    '''
    with _code_dir(), _venv(), _env():
        _run('celery multi restart phaceology_worker -A phaceology --pidfile="`pwd`/logs/celery-%n.pid" --logfile="`pwd`/logs/celery-%n%I.log"')

@task
@_show_in_titlebar
@roles('head', 'backup')
@parallel
def kick_apache():
    with _code_dir():
        _run("touch apache/*.wsgi")

@task
@_show_in_titlebar
@roles('head', 'backup')
@serial
def run_tests():
    with _code_dir(), _env():
        _run('scripts/maybe-update-venv.py')
    with _code_dir(), _env(), _venv():
        _run("env ./manage.py test %s --traceback --noinput" % env.tests)
    
@task
@_show_in_titlebar
@roles('head', 'backup')
def deploy():
    local_check_branch(env.branch)
    local_check_need_commit()
    local_check_need_push()
    execute(make_settings_json)
    execute(check_has_bower)
    execute(update_code)
    execute(copy_media)
    execute(head_deploy)
    execute(celery)
    execute(kick_apache)
    if not env.has_key('notest'):
        with settings(warn_only=True):
            execute(run_tests)



################################################################################
# Local Tasks

@task
@_localtask
@_show_in_titlebar
def local_manage(*args):
    '''
    Run a Django command from manage.py within the appropriate environment. The
    arguments must be specified using the Fabric convention, separated by
    commas, like follows:

    fab local_manage:validate,--no-input
    '''
    manage(*args)

@task
@_localtask
@_show_in_titlebar
def local_test():
    '''
    Run self-tests locally.
    '''
    run_tests()

@task
@_localtask
@_show_in_titlebar
def local_celery():
    with _code_dir(), _env(), _venv():
        _run('celery -A phaceology worker -l info')
        

@task
@_localtask
@_show_in_titlebar
def local_check_branch(expected):
    '''
    Verify that the local code is checked out to the correct branch (master if
    deploying to the master servers. development if deploying to the stage
    servers).
    '''
    with _code_dir():
        output = local('git rev-parse --abbrev-ref=loose HEAD', capture=True)
        if output != expected:
            abort('You are not on the correct branch. Expected "%s", got "%s". (Use "--set stage" to use the development branch.)' %
                  (expected, output))

@task
@_localtask
@_show_in_titlebar
def local_check_need_push():
    '''
    Verify that all local updates have been pushed to the remote repository. Can
    be disabled by setting the "uncommited" flag on the command line.
    '''
    log_output = local('git log origin/%s..%s' % (env.branch, env.branch), capture=True)
    print(log_output)
    if log_output:
        if env.get('uncommited'):
            warn('You have unpushed commits (see above). Ignoring them because you specified "--set uncommited".')
        else:
            abort('You have unpushed commits (see above). Please push them or run this command with the "--set uncommited" flag.')

@task
@_localtask
@_show_in_titlebar
def local_check_need_commit():
    '''
    Verify that all local updates have been commited. Can be disabled by setting
    the "uncommited" flag on the command line.
    '''
    with _code_dir():
        output = local('git status --porcelain', capture=True)
        print(output)
        if output:
            if env.get('uncommited'):
                warn('You have uncommited files (see above). Ignoring them because you specified "--set uncommited".')
            else:
                abort('You have uncommited files (see above). Please commit, remove, or stash them, or run this command with the "--set uncommited" flag.')

@task
@_localtask
@_show_in_titlebar
def local_check_has_bower():
    check_has_bower()


@task
@_localtask
@_show_in_titlebar
def local_copy_media():
    '''
    Copy demo media files to the proper location locally.
    '''
    with _code_dir():
        # MacOS does not have a '-u' option for the 'cp' command, so use rsync.
        local('rsync -avu demo_media/* media/')

@task
@_localtask
@_show_in_titlebar
def local_demodata():
    '''
    Create the demo account and lots of demo data.
    '''
    with _code_dir(), _venv(), _env():
        local('./manage.py demodata --traceback')

@task
@_localtask
@_show_in_titlebar
def local_deploy(frontend=True):
    '''
    Run the commands needed to get a local development environment ready to
    go. Assumes the code here and in server-config has already been updated from
    the Git repository. Also assumes this is only being run on one server at a
    time, since it performs the database syncing.
    '''
    with _code_dir(), _env():
        local('scripts/maybe-update-venv.py')
    head_deploy(frontend)
    make_settings_json()
    local_demodata()
    local_copy_media()

@task
@_localtask
@_show_in_titlebar
def local_collectstatic():
    with _code_dir(), _venv(), _env():
        local('./manage.py collectstatic -l --noinput --traceback')
    

@task
@_localtask
@_show_in_titlebar
def local_coverage():
    '''
    Run the test suite, creating a coverage report.
    '''
    #local_deploy()
    with _code_dir(), _venv(), _env():
        local("coverage run --source='.' --omit=='*/migrations/*,fabfile.py,env/*' manage.py test --traceback lp.tests")
        local('coverage html')
    print('Look in htmlcov/index.html for test coverage results.')


@task
@_localtask
@_show_in_titlebar
def local_runserver():
    local_deploy()
    with _code_dir(), _env(), _venv():
        local('./manage.py runserver --traceback')

@task
@_localtask
def local_make_settings_json():
    make_settings_json()

@task
@_localtask
def local_webpack():
    webpack()

@task
@_localtask
def local_webpackwatch():
    webpackwatch()

@task
@_localtask
def local_npm_install():
    npm_install()
