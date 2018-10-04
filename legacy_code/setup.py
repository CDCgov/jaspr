#!/usr/bin/env python
# file jaspr/setup.py

"""Compilation script for the jaspr package.

JASPR - James A Smagala's Program for Resistance.  A graphical tool
for simplifying data analysis for enzyme inhibition assays.  JASPR
was developed for the CDC Influenza Division's Molecular Epidemology
Team.

Revision History:
    20081020 James Smagala: hacked together from many other setup scripts
    20090203 JS: Heavy revisions to replace make.bat
    20090416 JS: Adding support for innosetup doubleclick installer and
                 renaming inhibition to jaspr

"""

from __future__ import with_statement

from distutils.core import setup
import py2exe
import sys
import os
import os.path
import subprocess
import shutil
import markdown
from datetime import datetime


def inno_script_setup(name, root, windows, install_path, icon,
                      version=datetime.now().strftime('%Y%m%d'),
                      iss_file_name=None):
    """Make an InnoScript compile script"""
    root = os.path.abspath(root)
    path = iss_file_name or name + '.iss'
    install_dir = os.path.join(install_path, name)

    # get a list of all the files to package
    all_files = []
    for walked_dir in os.walk(root):
        prefix = os.path.commonprefix((root, walked_dir[0], ))
        for file_name in walked_dir[2]:
            relative_path = walked_dir[0][len(prefix) + 1:]
            all_files.append(os.path.join(relative_path, file_name))

    # write out the script
    outfile = open(path, 'w')
    print >> outfile, '; WARNING: This script has been created by'
    print >> outfile, '; setup.py.  Changes to this script will be'
    print >> outfile, '; overwritten the next time setup.py is run!'
    print >> outfile, '[Setup]'
    print >> outfile, 'AppName=Install %s' % name
    print >> outfile, 'AppVerName=%s %s' % (name, version)
    print >> outfile, 'DefaultDirName=%s' % install_dir
    print >> outfile, 'DefaultGroupName=%s' % name
    print >> outfile, 'SetupIconFile=%s' % icon
    print >> outfile, ''

    print >> outfile, r"[Files]"
    for path in all_files:
        print >> outfile, r'Source: "%s"; DestDir: "{app}\%s"; Flags: '\
                          r'ignoreversion' % \
                          (os.path.join(name, path),
                           os.path.dirname(path))
    print >> outfile, ''

    print >> outfile, r"[Icons]"
    for window in windows:
        file_name = window['dest_base']
        path = file_name + '.exe'
        icon = os.path.normpath(window['icon_resources'][0][1])
        print >> outfile, r'Name: "{group}\%s"; Filename: '\
                          r'"{app}\%s"; IconFilename: "{app}\%s"' % \
                          (file_name, path, icon, )
        print >> outfile, r'Name: "{commondesktop}\%s"; Filename: '\
                          r'"{app}\%s"; WorkingDir: "{app}"; '\
                          r'IconFilename: "{app}\%s"' % \
                          (file_name, path, icon)
    print >> outfile, 'Name: "{group}\Uninstall %s"; Filename: '\
                      '"{uninstallexe}"; IconFilename: '\
                      '"{app}\icons\install.ico"'% name


def get_manifest():
    """Get a resouce manifest - gives apps a WinXP look if run on XP"""
    manifest_template = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
  />
  <description>%(prog)s</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
            level="asInvoker"
            uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="x86"
            publicKeyToken="1fc8b3b9a1e18e3b">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
  </dependency>
</assembly>
    
"""
    rt_manifest = 24
    return rt_manifest, manifest_template


def get_windows():
    """Get defs for GUI windows"""
    rt_manifest, manifest_template = get_manifest()
    jaspr = {
        'script': 'main/jaspr.py',
        'icon_resources': [(1, 'icons/graph.ico', ), ],
        'other_resources': [(rt_manifest, 1,
            manifest_template % {'prog': 'jaspr', }, ), ],
        'dest_base': 'jaspr',
    }
    windows = [jaspr, ]
    return windows


def get_console():
    """Get defs for console-only windows"""
    if not os.path.exists('bin'):
        return []
    else:
        return [os.path.join('bin', script) for script in os.listdir('bin')]


def get_options(project_name, includes, use_mpl=False):
    """Get the py2exe option dictionary"""
    dll_excludes = [
            # exclude tcl/tk if we are using matplotlib
            'iconv.dll',
            'intl.dll',
            'libatk-1.0-0.dll',
            'libgdk_pixbuf-2.0-0.dll',
            'libgdk-win32-2.0-0.dll',
            'libglib-2.0-0.dll',
            'libgmodule-2.0-0.dll',
            'libgobject-2.0-0.dll',
            'libgthread-2.0-0.dll',
            'libgtk-win32-2.0-0.dll',
            'libpango-1.0-0.dll',
            'libpangowin32-1.0-0.dll',
            # comment this out if os.popen() is used
            'w9xpopen.exe',
            # exclude here, include on a different path
            #'msvcp71.dll',
            #'msvcr71.dll',
            'msvcp90.dll',
            'msvcr90.dll', ]
    if use_mpl:
        dll_excludes.extend(['tk84.dll', 'tcl84.dll', ])
    # all of these excludes are for matplotlib
    excludes = [
            'Tkinter',
            'numarray',
            'Numeric',
            '_tkinter',
            '_gtkagg',
            '_tkagg',
            '_agg2',
            '_cairo',
            '_cocoaagg',
            '_fltkagg',
            '_gtk',
            '_gtkcairo',
            '_backend_gdk',
            '_gobject',
            '_tkinter',
            'glade',
            'pango',
            'QtCore',
            'QtGui', ]
    packages = ['gui', 'main', ]
    # fix dynamic import bug with reportlab
    packages.extend([
        'reportlab',
        'reportlab.graphics.charts',
        'reportlab.graphics.samples',
        'reportlab.graphics.widgets',
        'reportlab.graphics.barcode',
        'reportlab.graphics',
        'reportlab.lib',
        'reportlab.pdfbase',
        'reportlab.pdfgen',
        'reportlab.platypus', ])
    if use_mpl:
        packages.append('matplotlib')

    # actually build the options dictionary
    options = {'py2exe': {
            'compressed': 1,
            'optimize': 2,
            #'bundle_files': 1,
            #'ascii': 1, # this will exclude encodings, making
            #            # the file smaller, but it will
            #            # break if anything uses unicode
            'dist_dir': project_name,
            'dll_excludes': dll_excludes,
            'excludes': excludes,
            'includes': includes,
            'packages': packages, }, }
    return options


def get_data_files(project_name, includes):
    """Get any extra files that have not been included yet"""
    # check if we need matplotlib
    if 'matplotlib' in includes:
        from matplotlib import get_py2exe_datafiles
        data_files = get_py2exe_datafiles()
    else:
        data_files = []

    # include some MS dll files to reduce potential dependencies
    #dll_includes = ['dll/msvcp71.dll', 'dll/msvcr71.dll']
    dll_includes = ['dll/msvcp90.dll']
    data_files.append(('lib', dll_includes, ))

    # the zip file should be prebuilt in the build dir
    data_files.append(('source', ['build/%s_source.zip' % project_name, ], ))

    # any icons used by any of the programs go here
    icons = [os.path.join('icons', icon) for icon in os.listdir('icons')]
    data_files.append(('icons', icons, ))

    # include the config files
    config = [os.path.join('config', config)
            for config in os.listdir('config')]
    data_files.append(('config', config, ))

    # docs are assumed to be html formatted
    docs = [os.path.join('docs', doc) for doc in os.listdir('docs')
            if doc.endswith('html') or doc.endswith('doc')]
    data_files.append(('docs', docs, ))

    # css for for html docs
    css = [os.path.join('docs/blueprint', css) for css in
            os.listdir('docs/blueprint') if css.endswith('css')]
    data_files.append(('docs/blueprint', css, ))
    return data_files


def rm(path):
    """Remove a file, but don't error out if it doesn't exist"""
    try:
        os.remove(path)
    except OSError:
        pass


def rename(src, dst):
    """Remove a file, but don't error out if it doesn't exist"""
    try:
        os.rename(src, dst)
    except OSError:
        pass


def copy(src, dst):
    """Copy a file, but don't error out if it doesn't exist"""
    try:
        shutil.copy(src, dst)
    except OSError:
        pass
    except IOError:
        pass


def rmtree(path):
    """Remove a tree structure without error if it doesn't exist"""
    try:
        shutil.rmtree(path)
    except OSError:
        pass


def mkdir(path):
    """Create a directory, but don't error out if it already exists"""
    try:
        os.makedirs(path)
    except OSError:
        pass


def create_html_file(markdownfile, htmlfile):
    """Run markdown to convert to html, and add headers, etc"""
    header =  """<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 'Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <link rel="stylesheet" href="blueprint/screen.css" type="text/css" media="screen,projection" />
  <link rel="stylesheet" href="blueprint/print.css" type="text/css" media="print" />
  <!--[if IE]><link rel="stylesheet" href="blueprint/ie.css" type="text/css" media="screen,projection" /><![endif]-->
  <title>%s</title>
</head>
<body><div class="container"><div class="column span-24 last">""" % \
        os.path.splitext(os.path.basename(markdownfile))[0]

    with open(markdownfile, 'r') as md_handle:
        translated_text = markdown.markdown(md_handle.read())
    with open(htmlfile, 'w') as html_handle:
        print >> html_handle, header
        print >> html_handle, translated_text
        print >> html_handle, '</div></div></body>\n</html>'


def pre_compile_tasks(project_name):
    """Stuff to run before compiling"""

    def gen_html_docs():
        """Refresh the generated html documentation"""
        # regenerate the html documentation
        print 'Refresh the html documentation:',
        os.chdir('docs')
        for name in os.listdir(os.getcwd()):
            print '.',
            if name.endswith('.txt'):
                html_file = os.path.splitext(name)[0] + '.html'
                create_html_file(name, html_file)
        os.chdir('..')

    def build_source():
        """Copy over the source code, but don't copy revision history"""
        print '\nBuild the source .zip:',
        mkdir('build')
        top = os.getcwd()
        for root, dirs, files in os.walk(top):
            print '.',
            prefix = os.path.commonprefix((top, root, ))
            rel_root = root[len(prefix) + 1:]
            if root == top:
                for dir in ('build', '.hg', project_name, ):
                    if dir in dirs:
                        del dirs[dirs.index(dir)]
            new_path = os.path.join('build', project_name, rel_root)
            mkdir(new_path)
            for name in files:
                if name.startswith('.') or name.endswith('.swp') or \
                        name.endswith('.pyc') or name.endswith('.html'):
                    continue
                shutil.copy(os.path.join(root, name),
                            os.path.join(new_path, name))

    def zip_source():
        """Zip the source up so it can be included when compiling"""
        print '\nBuild the source.zip files:'
        os.chdir('build')
        subprocess.call(['zip', '-r', '-m', '%s_source.zip' % project_name, 
                '%s/' % project_name, ])
        os.chdir('..')

    gen_html_docs()
    build_source()
    zip_source()


def post_compile_tasks(windows, project_name, install_path, version):
    """Build an automatic install script and manual zip file"""
    # make an inno setup .iss script
    iss_name = 'Install %s %s' % (project_name, version)
    inno_script_setup(name=project_name, root=project_name,
                      windows=windows, install_path=install_path,
                      icon=r'icons\install.ico', version=version,
                      iss_file_name='%s.iss' % iss_name)

    # compile the .iss script to an exe installer
    subprocess.call(['ISCC.exe', '/O%s' % os.getcwd(),
            '/F%s' % iss_name,
            '%s.iss' % iss_name, ])

    # zip up the files for manual installation
    subprocess.call(['zip', '-r', '-m', '%s %s.zip' % \
            (project_name, version), project_name, ])


def clean(project_name=None):
    """clean up previous compilations and build source bundles"""
    print '\nClean-up old files:',
    if project_name:
        rmtree(project_name)
    print '.',
    rmtree('build')
    print '.',

    for root, dirs, files in os.walk(os.getcwd()):
        # don't screw with mercurial stuff
        if root == os.getcwd():
            try:
                del dirs[dirs.index('.hg')]
            except ValueError:
                pass
        print '.',
        # clean up all other dirs of any generated files
        for name in files:
            if name.endswith('.html') or name.endswith('.iss') or \
                    name.endswith('.pyc') or name.endswith('.zip') or \
                    name.endswith('.exe'):
                rm(os.path.join(root, name))
    print '.'


def compile():
    """Run the setup/py2exe compilation"""
    # add the current dir to the python path to make it easier to
    # find all of the various packages we want
    sys.path.append(os.getcwd())

    # packages that we want to include
    # FIXME experiment with removing some of these
    includes = ['wx', 'matplotlib', 'numpy', 'scipy', 'scipy.linalg.*',
            'scipy.sparse.csgraph._validation', 'scipy.special.*',
            'scipy.integrate', 'sip']

    # minimize the number of places where this has to be changed to
    # adapt the script for compiling a new package - note that this
    # should not contain spaces
    project_name = 'jaspr'
    version = 'v1.3'

    install_path = r'C:\Program Files'
    clean(project_name)
    pre_compile_tasks(project_name)
    print 'Compiling:'
    windows = get_windows()

    # as if we included py2exe on the command line - this will
    # allow us to run the script by double clicking
    sys.argv.append('py2exe')

    # actually run the distutils setup
    # we should only have to edit packages, project_name, and the
    # get_windows function (requires too much customization to
    # automate)
    setup(
        console = get_console(),
        options = get_options(project_name, includes, use_mpl=True),
        windows = windows,
        zipfile = 'lib/%s.lib' % project_name,
        data_files = get_data_files(project_name, includes), )

    # run the post-compile tasks to move compiled files
    post_compile_tasks(windows, project_name, install_path, version)


if __name__ == '__main__':

    def main():
        """Run the compliation if setup is run with no args"""
        if 'clean' in sys.argv:
            clean('jaspr')
        else:
            compile()

    main()
