import paver
from paver.easy import *
from socket import gethostname
import paver.setuputils
paver.setuputils.install_distutils_tasks()
from os import environ
import os.path

######## CHANGE THIS ##########
project_name = "webfundamentals"
###############################

# if you want to override the master url do it here.  Otherwise setting it to None
# configures it for the default case of wanting to use localhost for development
# and interactivepython for deployment

master_url = None
if master_url is None:
    if gethostname() in ['web407.webfaction.com', 'rsbuilder']:
        master_url = 'http://interactivepython.org'
    else:
        master_url = 'http://127.0.0.1:8000'

master_app = 'runestone'
serving_dir = './build/webfundamentals'
dest = '../../static'

options(
    sphinx = Bunch(docroot=".",),

    gettext = Bunch(
        builder='gettext',
        builddir='./build/'+project_name,
        outdir='./locale/pot',
        #templates='pkg',
        sourcedir='./_sources/',
        doctrees='./gettext/doctrees/',
        docroot='.',
        confdir=".",
        warnerror=False,
        template_args = {
            'course_id':project_name,
        }
    ),

    build = Bunch(
        builddir="./build/"+project_name,
        sourcedir="_sources",
        outdir="./build/"+project_name,
        confdir=".",
        project_name = project_name,
        template_args = {
            'course_id':project_name,
            'login_required':'false',
            'appname':master_app,
            'loglevel':10,
            'course_url':master_url,
            'use_services': 'true',
            'python3': 'true',
            'dburl': 'postgresql://bmiller@localhost/runestone',
            'basecourse': 'webfundamentals',
        }
    )
)

# Check to see if we are building on our Jenkins build server, if so use the environment variables
# to update the DB information for this build
if 'DBHOST' in environ and  'DBPASS' in environ and 'DBUSER' in environ and 'DBNAME' in environ:
    options.build.template_args['dburl'] = 'postgresql://{DBUSER}:{DBPASS}@{DBHOST}/{DBNAME}'.format(**environ)

from runestone import build  # build is called implicitly by the paver driver.

@task
def gettext(options):
    "Collect all translatable strings from rst input."
    # Create output directory & separate doctree directory
    for dir in (options.gettext.outdir, os.path.dirname(options.gettext.doctrees)):
	if not os.path.exists(dir):
            os.makedirs(dir)
    # Extract messages (POT)
    options.order('gettext', 'sphinx', add_rest=True)
    from sphinxcontrib import paverutils
    paverutils.run_sphinx(options, "gettext")
    # Update translations PO: TODO: read conf["locale_dirs"][0] & language (es)
    sh('sphinx-intl update -p "%s" --locale-dir locale -l es' % (options.gettext.outdir, ))
    # Remember to build the MO files once translated:
    sh('sphinx-intl build --locale-dir locale')
    return
