
####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2019 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

from pathlib import Path
import os
import shutil

from invoke import task
 # import sys

from .release import update_git_sha as _update_git_sha

####################################################################################################

KICADRW_SOURCE_PATH = Path(__file__).resolve().parents[1]

EXAMPLES_PATH = KICADRW_SOURCE_PATH.joinpath('examples')

SPHINX_PATH = KICADRW_SOURCE_PATH.joinpath('doc', 'sphinx')
BUILD_PATH = SPHINX_PATH.joinpath('build')
RST_SOURCE_PATH = SPHINX_PATH.joinpath('source')
RST_API_PATH = RST_SOURCE_PATH.joinpath('api')
RST_EXAMPLES_PATH = RST_SOURCE_PATH.joinpath('examples')

####################################################################################################

@task
def clean_build(ctx):
    # ctx.run('rm -rf {}'.format(BUILD_PATH))
    if BUILD_PATH.exists():
        shutil.rmtree(BUILD_PATH)

####################################################################################################

@task
def clean_api(ctx):
    # ctx.run('rm -rf {}'.format(RST_API_PATH))
    if RST_API_PATH.exists():
        shutil.rmtree(RST_API_PATH)

@task(_update_git_sha, clean_api)
def make_api(ctx):
    print('\nGenerate RST API files')
    ctx.run('pyterate-rst-api {0.Package}'.format(ctx))
    run_sphinx(ctx)

####################################################################################################

@task(_update_git_sha)
def make_examples(ctx, clean=False, no_html=False, force=False):

    # Regenerate from scratch
    if clean and RST_EXAMPLES_PATH.exists():
        shutil.rmtree(RST_EXAMPLES_PATH)

    # pyterate --skip-external-figure --skip-figure
    # PYTHONPATH=$PWD/examples/:${PYTHONPATH}
    # KiCadRWLogLevel=WARNING

    os.environ['KiCadRWLibraryPath'] = str(EXAMPLES_PATH.joinpath('libraries'))
    os.environ['KiCadRWLogLevel'] = 'ERROR'  # set logging level

    setting_path = EXAMPLES_PATH.joinpath('Settings.py')
    # subprocess.run(('pyterate',
    #                 '--config', str(setting_path))
    # )
    print('Generate RST examples files')
    command = [
        'pyterate',
        '--config={}'.format(setting_path),
    ]
    if force:
        command.append('--force')
    ctx.run(' '.join(command))

    if not no_html:
        run_sphinx(ctx)

####################################################################################################

@task
def run_sphinx(ctx):
    print('\nRun Sphinx')
    working_path = SPHINX_PATH
    # subprocess.run(('make-html'), cwd=working_path)
    # --clean
    with ctx.cd(str(working_path)):
        ctx.run('make-html')

####################################################################################################

@task
def make_readme(ctx):
    # File "/usr/bin/rst2html", line 17, in <module>
    # from docutils.core import publish_cmdline, default_description
    # ModuleNotFoundError: No module named 'docutils'
    from setup_data import long_description
    with open('README.rst', 'w') as fh:
        fh.write(long_description)
    # import subprocess
    # subprocess.call(('rst2html', 'README.rst', 'README.html'))
    ctx.run('rst2html5.py README.rst README.html')
    ctx.run('pandoc -t gfm --columns=100 -o README.md README.rst')

####################################################################################################

@task
def update_authors(ctx):
    # Keep authors in the order of appearance and use awk to filter out dupes
    ctx.run("git log --format='- %aN <%aE>' --reverse | awk '!x[$0]++' > AUTHORS")

####################################################################################################

@task
def publish(ctx):
    from .SECRET_CONFIG import SSH_CONFIG
    import kicadrw
    release = KiCadRW.__version__
    version = '.'.join(release.split('.')[:2])
    command_template = (
        'rsync'
        ' -av -c --delete'
        ' --exclude="*~" --delete-excluded'
        ' -e "ssh -p {ssh_port}" {src_path}/ {ssh_user}@{ssh_host}:{ssh_path}/releases/v{version}/'
    )
    command = command_template.format(
        src_path=BUILD_PATH.joinpath('html'),
        version=version,
        **SSH_CONFIG)
    print(command)
    ctx.run(command)

####################################################################################################

@task
def xdg_open(ctx):
    ctx.run('xdg-open doc/sphinx/build/html/index.html')
