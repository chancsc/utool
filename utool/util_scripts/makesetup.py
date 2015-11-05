#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os
import utool
from os.path import basename


def make_setup(repodir):
    setup_text_fmt_ = '''
    # autogenerated setup.py on {timestamp} for {repodir}
    from __future__ import absolute_import, division, print_function
    import setuptools
    #from utool import util_setup

    INSTALL_REQUIRES = [
    ]

    if __name__ == '__main__':
        setuptools.setup(
            name='{pkgname}',
            packages={packages},
            #packages=util_setup.find_packages(),
            #version='0.0.0.autogen',
            #description='short description',
            #url='',
            #ext_modules=util_setup.find_ext_modules(),
            #cmdclass=util_setup.get_cmdclass(),
            #author=''
            #author_email='',
            #keywords='',
            #install_requires=INSTALL_REQUIRES,
            package_data={{}},
            scripts=[
            ],
            classifiers=[],
        )
    '''
    setup_text_fmt = utool.unindent(setup_text_fmt_)
    timestamp = utool.get_timestamp()
    pkgname = basename(repodir)
    packages = utool.ls_moduledirs(repodir, full=False)
    print(pkgname)
    setup_text = setup_text_fmt.format(
        packages=packages,
        repodir=repodir,
        timestamp=timestamp,
        pkgname=pkgname,
    )
    return setup_text


if __name__ == '__main__':
    writeflag = utool.get_argflag(('--write', '-w'))
    overwriteflag = utool.get_argflag(('--yes', '-y'))
    repodir = utool.unixpath(os.getcwd())
    print('[utool] making setup.py for: %r' % repodir)
    setup_text = make_setup(repodir)
    if writeflag:
        setup_fpath = utool.unixjoin(repodir, 'setup.py')
        if utool.checkpath(setup_fpath):
            confirm_flag = overwriteflag
        else:
            confirm_flag = True
        if confirm_flag:
            utool.write_to(setup_fpath, setup_text)
        else:
            print('setup.py file exists not writing')
    else:
        print(setup_text)
