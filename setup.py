"""PyQ: Python/Q Integration

PyQ provides seamless integration of Python and Q code. It brings
Python and Q interpreters in the same process and allows code written
in either of the languages to operate on the same data. In PyQ, Python
and Q objects live in the same memory space and share the same data.
"""
import os
import struct
import sys
from subprocess import check_output, call
from distutils.ccompiler import new_compiler, CCompiler
from distutils.util import get_platform
from os.path import join
from distutils import log
from stat import ST_MODE

try:
    from setuptools import Extension
    from setuptools import setup, Command
    from setuptools import Distribution as _Distribution
    from setuptools.command.install_lib import install_lib as _install_lib
    from setuptools.command.install import install as _install
except ImportError:
    from distutils.core import Extension
    from distutils.core import setup, Command
    from distutils.core import Distribution as _Distribution
    from distutils.command.install_lib import install_lib as _install_lib
    from distutils.command.install import install as _install
from distutils.command.build import build as _build
from distutils.command.config import config as _config
from distutils.command.build_ext import build_ext as _build_ext
from distutils.sysconfig import customize_compiler, get_config_var, get_python_inc
from distutils.command.install_scripts import install_scripts as _install_scripts

try:
    from os import uname
except ImportError:
    # NB: Windows does not support os.uname, need to use platform.uname.
    from platform import uname


VERSION = '4.0.3'
IS_RELEASE = True
PYQ_SRC_DIR = os.path.join('src', 'pyq')
VERSION_FILE = os.path.join(PYQ_SRC_DIR, 'version.py')
BITS = struct.calcsize('P') * 8


metadata = dict(
    name='pyq',
    packages=['pyq', 'pyq.tests', ],
    scripts=['src/scripts/pyq-runtests',
             'src/scripts/pyq-coverage',
             'src/scripts/ipyq',
             'src/scripts/pq',
             'src/scripts/qp',
             ],
    url='http://pyq.enlnt.com',
    author='Enlightenment Research, LLC',
    author_email='pyq@enlnt.com',
    license='PyQ General License',
    platforms=['Linux', 'Mac OS-X', 'Solaris'],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Financial and Insurance Industry',
                 'Intended Audience :: Science/Research',
                 'License :: Other/Proprietary License',
                 'Natural Language :: English',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: POSIX :: Linux',
                 'Operating System :: POSIX :: SunOS/Solaris',
                 'Programming Language :: C',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Topic :: Database',
                 'Topic :: Software Development :: Libraries :: Python Modules'],
)


if str is bytes:
    def decode(x):
        return x
else:
    def decode(x):
        return x.decode()

k_extra_compile_args = ['-Wpointer-arith', '-Werror', '-fno-strict-aliasing']
py_extra_compile_args = ['-O0', '-g']
extra_link_args = []
libraries = []

platform = uname()[0]
if platform == 'Darwin':
    out = check_output(['otool', '-L', sys.executable])
    for line in out.splitlines():
        if b'libpython' in line:
            pypath = decode(line.split()[0])
            python_lib_dir = os.path.dirname(pypath)
            break
        if b'Python' in line:
            pypath = decode(line.split()[0])
            pypath = pypath.replace('@executable_path', os.path.dirname(sys.executable))
            # while os.path.islink(pypath):
            #    pypath = os.readlink(pypath)
            python_lib_dir = os.path.join(os.path.dirname(pypath), 'lib')
            break
    else:
        python_lib_dir = '/System/Library/Frameworks/Python.framework/Versions/%s/lib' % sys.version[0:3]
elif platform.startswith(('Linux', 'SunOS')):
    out = check_output(['ldd', sys.executable])
    for line in out.splitlines():
        if b'libpython' in line:
            pypath = decode(line.split()[2])
            python_lib_dir = os.path.dirname(pypath)
            break
    else:
        python_lib_dir = os.path.join(sys.exec_prefix, 'lib')
elif platform == 'Windows':
    python_lib_dir = os.path.join(sys.exec_prefix, 'libs')
    libraries = ['python%s%s' % sys.version_info[:2]]
    k_extra_compile_args = []
    py_extra_compile_args = []
    extra_link_args = [os.path.join(PYQ_SRC_DIR, 'w%i' % BITS, 'q.lib')]
else:
    raise ValueError('PyQ is not supported under %s.' % platform)


def get_version():
    if IS_RELEASE:
        version = VERSION
    elif os.path.exists('.git'):
        try:
            out = check_output(['git', 'describe'])
            tag, commits, revision = decode(out).strip().split('-')
            version = VERSION + '.dev{}+{}'.format(commits, revision[1:])
        except (OSError, ValueError):
            version = VERSION + '.dev0+unknown'
    elif os.path.exists(VERSION_FILE):
        import imp
        ver = imp.load_source('pyq.version', VERSION_FILE)
        version = ver.version
    else:
        version = VERSION + '.dev0+unknown'

    version_code = "# generated by setup.py\nversion = '{}'\n".format(version)
    with open(VERSION_FILE, 'w') as f:
        f.write(version_code)
    return version


pyq_version = get_version()

_k = Extension('pyq._k',
               sources=[os.path.join(PYQ_SRC_DIR, '_k.c'), ],
               extra_compile_args=k_extra_compile_args,
               include_dirs=[],
               extra_link_args=extra_link_args, )
py = Extension('py',
               sources=[os.path.join(PYQ_SRC_DIR, 'py.c'), ],
               extra_compile_args=py_extra_compile_args,
               runtime_library_dirs=[python_lib_dir],
               library_dirs=[python_lib_dir],
               libraries=libraries,
               extra_link_args=extra_link_args, )
p = Extension('p',
              sources=[os.path.join(PYQ_SRC_DIR, 'p.c'), ],
              extra_compile_args=[],
              runtime_library_dirs=[python_lib_dir],
              library_dirs=[python_lib_dir], )


class Executable(object):
    def __init__(self, name, sources,
                 include_dirs=None, define_macros=None, libraries=None):
        self.name = name
        self.sources = sources
        self.include_dirs = include_dirs or []
        self.define_macros = define_macros or []
        self.libraries = libraries or []


metadata.update(
    executables=[Executable('pyq', ['src/pyq.c'])],
    q_modules=['python', 'pyq-operators'],
    k_modules=['p'],
    ext_modules=[_k, ],
    qext_modules=[py, p, ],
)


class config(_config):
    def run(self):
        self.check_lib('python' + sys.version[:3])


class build(_build):
    user_options = _build.user_options + [
        ('build-qlib=', None,
         "build directory for q/k modules"),
        ('build-qext=', None,
         "build directory for q extension modules"),
    ]
    user_options.sort()

    def initialize_options(self):
        _build.initialize_options(self)
        self.build_exe = None
        self.build_qlib = None
        self.build_qext = None

    def finalize_options(self):
        _build.finalize_options(self)
        plat_specifier = ".%s-%s" % (self.plat_name, sys.version[:3])

        if self.build_exe is None:
            self.build_exe = os.path.join(self.build_base,
                                          'exe' + plat_specifier)
        if self.build_qlib is None:
            self.build_qlib = os.path.join(self.build_base,
                                           'qlib' + plat_specifier)
        qarch = self.distribution.qarch
        kxver = self.distribution.kxver
        if self.build_qext is None:
            self.build_qext = os.path.join(self.build_base,
                                           'qext.%s-%s' % (qarch, kxver))
        self.build_temp += '-kx-' + kxver.split('.')[0]

    def has_qk_modules(self):
        return self.distribution.has_qlib()

    def has_qext(self):
        return self.distribution.has_qext()

    def has_exe(self):
        return self.distribution.has_exe()

    sub_commands = _build.sub_commands + [
        ('build_qk', has_qk_modules),
        ('build_qext', has_qext),
        ('build_exe', has_exe),
    ]


class build_exe(Command):
    description = "builds executable"
    user_options = []

    def __init__(self, dist):
        self.compiler = None
        Command.__init__(self, dist)

    def initialize_options(self):
        self.build_temp = None
        self.build_lib = None

    def finalize_options(self):
        self.set_undefined_options('build_ext',
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'), )

        if not self.build_lib:
            self.build_lib = self._get_build_lib()

    def _get_build_lib(self):
        # More distutils hackishness.  The build.build_lib changes depending on whether
        # ext_modules is empty or not.  For us, obviously it is empty.  Therefore we had to
        # duplicate it.
        return join('build', 'exe.{}-{}'.format(get_platform(), sys.version[0:3]))

    def run(self):
        for exe in self.distribution.executables:
            exe.include_dirs.append(get_python_inc())
            compiler = new_compiler(  # compiler=self.compiler,
                verbose=self.verbose,
                dry_run=self.dry_run,
                force=self.force)
            customize_compiler(compiler)
            compiler.set_include_dirs(exe.include_dirs)
            for (name, value) in exe.define_macros:
                compiler.define_macro(name, value)

            objects = compiler.compile(exe.sources, output_dir=self.build_temp)

            # This is a hack copied from distutils.commands.build_exe (where it is also called
            # a hack).
            self._build_objects = objects[:]

            library_dirs = [os.path.join(sys.exec_prefix, 'lib')]

            exe_path = join(self.build_lib, exe.name.split('.')[-1])

            compiler.link(CCompiler.EXECUTABLE,
                          objects=objects,
                          output_filename=exe_path,
                          library_dirs=library_dirs,
                          libraries=exe.libraries,
                          extra_preargs=['-m32'] if BITS == 32 else [],
                          )


class build_qk(Command):
    description = "build pure Q/K modules"

    user_options = [
        ('build-lib=', 'd', "build directory"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
    ]

    def initialize_options(self):
        self.build_lib = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_qlib', 'build_lib'),
                                   ('force', 'force'))
        # Get the distribution options that are aliases for build_qk
        # options -- list of Q/K modules.
        self.q_modules = self.distribution.q_modules
        self.k_modules = self.distribution.k_modules
        pyver = sys.version[0:3] + getattr(sys, 'abiflags', '')
        self.pyver_rule = (None, 'PYVER:', 'PYVER:"%s"\n' % pyver)
        qpath = self.distribution.qexecutable
        if self.distribution.kxver >= '2.3':
            self.qpath_rule = (0, '#!', "#! %s\n" % qpath)
        else:
            self.qpath_rule = (0, '#!', "")
        self.q_module_rules = [self.qpath_rule, self.pyver_rule]
        # PyQ version rule
        self.q_module_rules.append((None, 'VER:', 'VER:"%s"\n' % get_version()))
        soabi = get_config_var('SOABI')
        if soabi:
            self.q_module_rules.append((None, 'PYSO:', 'PYSO:`$"py.%s"\n' % soabi))
            self.q_module_rules.append((None, 'PSO:', 'PSO:`$"p.%s"\n' % soabi))

        # FIXME: Windows
        soext = '.dylib\\000' if platform == 'Darwin' else '.so\\000'
        self.q_module_rules.append((None, 'SOEXT:', 'SOEXT: "%s"\n' % soext))
        virtual_env = os.getenv('VIRTUAL_ENV')

        if virtual_env:  # Issue #627
            python_path = os.path.join(virtual_env, 'bin', 'pyq')
        else:
            # TODO: Figure better way getting path to pyq script when will fail.
            python_path = sys.executable + '.py'

        self.q_module_rules.append((None, 'PYTHON:', 'PYTHON: "%s"\n' % python_path))

        if platform == 'Darwin':  # Issue #559
            if virtual_env:
                if sys.version_info[0] < 3:
                    lib_string = 'lib:"%s\\000"\n' % os.path.join(virtual_env, '.Python')
                else:
                    lib_string = 'lib:"%s\\000"\n' % pypath
                self.q_module_rules.append((None, 'lib:', lib_string))

    def run(self):
        self.mkpath(self.build_lib)
        for m in self.q_modules:
            filename = m + '.q'
            infile = os.path.join(PYQ_SRC_DIR, filename)
            outfile = os.path.join(self.build_lib, filename)
            self.build_q_module(infile, outfile)
        for m in self.k_modules:
            filename = m + '.k'
            infile = os.path.join(PYQ_SRC_DIR, filename)
            outfile = os.path.join(self.build_lib, filename)
            self.build_k_module(infile, outfile)

    def build_k_module(self, infile, outfile):
        self.build_module(infile, outfile, self.q_module_rules)

    def build_q_module(self, infile, outfile):
        self.build_module(infile, outfile, self.q_module_rules)
        # copy executable flags
        inmode = os.stat(infile).st_mode
        if inmode & 0o111:
            outmode = os.stat(outfile).st_mode
            os.chmod(outfile, inmode & 0o111 | outmode)

    def build_module(self, infile, outfile, rules):
        adjust = {}
        sentinel = object()
        with open(infile) as source:
            for lineno, line in enumerate(source):
                if not line.strip():
                    adjust[lineno] = sentinel
                    break
                for rlineno, start, adjusted in rules:
                    if (rlineno is None or
                                lineno == rlineno) and line.startswith(start):
                        adjust[lineno] = adjusted
        if adjust:
            with open(infile) as source:
                with open(outfile, 'w') as target:
                    for lineno, line in enumerate(source):
                        a = adjust.get(lineno)
                        if a is sentinel:
                            target.write("/ ^^^ generated by setup ^^^\n")
                            target.writelines(source)
                            break
                        if a is None:
                            target.write(line)
                        else:
                            target.write(a)
        else:
            self.copy_file(infile, outfile, preserve_mode=0)


class build_ext(_build_ext):
    def get_ext_filename(self, ext_name):
        filename = _build_ext.get_ext_filename(self, ext_name)
        so_ext = get_config_var('SO')
        return filename[:-len(so_ext)] + so_ext

    def get_export_symbols(self, ext):
        initfunc_name = "init" + ext.name.split('.')[-1]
        if initfunc_name not in ext.export_symbols:
            ext.export_symbols.append(initfunc_name)
        return ext.export_symbols


class build_qext(_build_ext):
    description = "build Q extension modules"

    user_options = [
        ('build-lib=', 'd', "build directory"),
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
    ]

    def get_ext_filename(self, ext_name):
        filename = _build_ext.get_ext_filename(self, ext_name)
        so_ext = get_config_var('SO')
        soabi = get_config_var('SOABI')
        if sys.version_info < (3, 5) and soabi and platform == 'Darwin':
            filename = "%s.%s%s" % (filename[:-len(so_ext)], soabi, so_ext)
        return filename

    def swig_sources(self, sources, ext):
        return sources

    def finalize_options(self):
        from distutils import sysconfig

        self.set_undefined_options('build',
                                   ('build_qext', 'build_lib'),
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('force', 'force'),
                                   ('plat_name', 'plat_name'),
                                   )
        self.extensions = self.distribution.qext_modules

        # TODO: Don't add python stuff to q extentions that don't need it
        # Make sure Python's include directories (for Python.h, pyconfig.h,
        # etc.) are in the include search path.
        py_include = sysconfig.get_python_inc()
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        if self.include_dirs is None:
            self.include_dirs = self.distribution.include_dirs or []
        if isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        # Put the Python "system" include dir at the end, so that
        # any local include dirs take precedence.
        self.include_dirs.append(py_include)
        if plat_py_include != py_include:
            self.include_dirs.append(plat_py_include)
        self.ensure_string_list('libraries')

        # Life is easier if we're not forever checking for None, so
        # simplify these options to empty lists if unset
        if self.libraries is None:
            self.libraries = []
        if self.library_dirs is None:
            self.library_dirs = []
        elif isinstance(self.library_dirs, str):
            self.library_dirs = self.library_dirs.split(os.pathsep)

        if self.rpath is None:
            self.rpath = []
        elif isinstance(self.rpath, str):
            self.rpath = self.rpath.split(os.pathsep)

        if self.define:
            defines = [dfn.split(':') for dfn in self.define.split(',')]
            self.define = [(dfn if len(dfn) == 2 else dfn + ['1'])
                           for dfn in defines]
        else:
            self.define = []
        if self.undef:
            self.undef = self.undef.split(',')

    def run(self):
        from distutils.ccompiler import new_compiler

        if not self.extensions:
            return
            # Setup the CCompiler object that we'll use to do all the
        # compiling and linking
        self.compiler = new_compiler(compiler=self.compiler,
                                     verbose=self.verbose,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)
        # And make sure that any compile/link-related options (which might
        # come from the command-line or from the setup script) are set in
        # that CCompiler object -- that way, they automatically apply to
        # all compiling and linking done here.
        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for (name, value) in self.define:
                self.compiler.define_macro(name, value)
        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)
        if self.libraries is not None:
            self.compiler.set_libraries(self.libraries)
        if self.library_dirs is not None:
            self.compiler.set_library_dirs(self.library_dirs)
        if self.rpath is not None:
            self.compiler.set_runtime_library_dirs(self.rpath)
        if self.link_objects is not None:
            self.compiler.set_link_objects(self.link_objects)

        # Now actually compile and link everything.
        self.build_extensions()


class install_qlib(_install_lib):
    description = "install Q/K modules"

    def run(self):
        if not self.skip_build:
            self.run_command('build_qk')
        self.mkpath(self.install_dir)
        self.copy_tree(self.build_dir, self.install_dir)

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('build_qlib', 'build_dir'),
                                   ('install_qlib', 'install_dir'),
                                   ('force', 'force'),
                                   ('compile', 'compile'),
                                   ('skip_build', 'skip_build'),
                                   )
        self.optimize = 0
        if self.install_dir is None:
            self.install_dir = self.distribution.qhome

    def get_outputs(self):
        # import pdb; pdb.set_trace()
        build = self.get_finalized_command('build_qk')
        q_files = [m + '.q' for m in build.q_modules]
        k_files = [m + '.k' for m in build.k_modules]
        return [os.path.join(self.install_dir, f) for f in q_files + k_files]


class install_qext(_install_lib):
    description = "install q extension modules"

    def run(self):
        if not self.skip_build:
            self.run_command('build_qext')
        self.mkpath(self.install_dir)
        outfiles = self.copy_tree(self.build_dir, self.install_dir)

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('build_qext', 'build_dir'),
                                   ('install_qext', 'install_dir'),
                                   ('force', 'force'),
                                   ('compile', 'compile'),
                                   ('skip_build', 'skip_build'),
                                   )
        self.optimize = 0
        if self.install_dir is None:
            self.install_dir = self.distribution.qhome

        if platform == 'Darwin' and BITS == 64 and \
                not os.path.exists(self.install_dir):
            # This is a hack to make 32-bit q work on 64-bit Mac for testing purposes.
            qhome_m32 = os.path.join(self.distribution.qhome, 'm32')
            if os.path.exists(qhome_m32):
                self.install_dir = qhome_m32

    def get_outputs(self):
        build = self.get_finalized_command('build_qext')
        return [os.path.join(self.install_dir, os.path.basename(f)) for f in build.get_outputs()]


class install_exe(_install_scripts):
    description = "install executables"

    def finalize_options(self):
        self.set_undefined_options('build', ('build_exe', 'build_dir'))
        self.set_undefined_options('install',
                                   ('install_scripts', 'install_dir'),
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'),
                                   )

    def run(self):
        if not self.skip_build:
            self.run_command('build_exe')
        self.outfiles = self.copy_tree(self.build_dir, self.install_dir)
        if os.name == 'posix':
            # Set the executable bits (owner, group, and world) on
            # all the scripts we just installed.
            for file in self.get_outputs():
                if self.dry_run:
                    log.info("changing mode of %s", file)
                else:
                    mode = ((os.stat(file)[ST_MODE]) | 0o555) & 0o7777
                    log.info("changing mode of %s to %o", file, mode)
                    os.chmod(file, mode)

    def get_inputs(self):
        return self.distribution.scripts or []

    def get_outputs(self):
        return self.outfiles or []


class install(_install):
    def has_exe(self):
        return self.distribution.has_exe()

    def has_qlib(self):
        return self.distribution.has_qlib()

    def has_qext(self):
        return self.distribution.has_qext()

    def initialize_options(self):
        self.install_qlib = None
        self.build_qlib = None
        self.build_exe = None
        self.install_exe = None
        self.install_qext = None
        self.build_qext = None
        _install.initialize_options(self)

    def finalize_options(self):
        _install.finalize_options(self)
        self.set_undefined_options('build',
                                   ('build_qlib', 'build_qlib'),
                                   ('build_qext', 'build_qext'),
                                   )
        dst = self.distribution
        if self.install_qlib == None:
            self.install_qlib = dst.qhome
        if self.install_qext == None:
            self.install_qext = os.path.join(dst.qhome, dst.qarch)

    user_options = _install.user_options + [
        ('install-qlib=', None,
         "installation directory for all Q/K module distributions"),
        ('install-qext=', None,
         "installation directory for Q extension module distributions"),
    ]

    sub_commands = _install.sub_commands + [
        ('install_exe', has_exe),
        ('install_qlib', has_qlib),
        ('install_qext', has_qext),
    ]


class PyTest(Command):  # from http://pytest.org/latest/goodpractises.html
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = call(['python.q', 'pyq-runtests'])
        raise SystemExit(errno)


class Distribution(_Distribution):
    def __init__(self, attrs=None):
        self.k_modules = None
        self.q_modules = None
        self.qext_modules = None
        self.executables = None
        _Distribution.__init__(self, attrs)

    def has_exe(self):
        return bool(self.executables)

    def has_qlib(self):
        return self.k_modules or self.q_modules

    def has_qext(self):
        return bool(self.qext_modules)

    def get_kxver(self, qhome):
        """Determine version of q installed at qhome
        """
        qk = os.path.join(qhome, 'q.k')
        with open(qk) as source:
            for line in source:
                if line.startswith('k:'):
                    return line[2:5]
        return '2.2'

    def finalize_options(self):
        self.cmdclass['config'] = config

        self.cmdclass['build'] = build
        self.cmdclass['build_exe'] = build_exe
        self.cmdclass['build_qk'] = build_qk
        self.cmdclass['build_ext'] = build_ext
        self.cmdclass['build_qext'] = build_qext

        self.cmdclass['install'] = install
        self.cmdclass['install_exe'] = install_exe
        self.cmdclass['install_qlib'] = install_qlib
        self.cmdclass['install_qext'] = install_qext

        self.cmdclass['test'] = PyTest

        if 'QHOME' in os.environ:
            self.qhome = os.getenv('QHOME')
        else:
            qhome_root = os.getenv('SystemDrive') + '\\' if platform == 'Windows' else os.getenv('HOME')
            self.qhome = os.path.join(qhome_root, 'q')
            if 'VIRTUAL_ENV' in os.environ:
                path = os.path.join(os.getenv('VIRTUAL_ENV'), 'q')
                if os.path.exists(path):
                    self.qhome = path

        bits = BITS
        if platform == 'Linux':
            o = 'l'
        elif platform == 'SunOS':
            o = 'v' if uname()[-1] == 'i86pc' else 's'
        elif platform == 'Darwin':
            o = 'm'
            bits = 32
        elif platform == 'Windows':
            o = 'w'
            bits = 32  # FIXME: We test with 32-bit kdb+ on Windows, so forcing 32-bit version.
        else:
            sys.stderr.write("Unknown platform: %s\n" % str(platform))
            sys.exit(1)
        self.qarch = "%s%d" % (o, bits)
        self.install_data = os.path.join(self.qhome, self.qarch)
        self.kxver = self.get_kxver(self.qhome)
        self.qexecutable = os.path.join(self.qhome, self.qarch, 'q')
        _Distribution.finalize_options(self)
        for ext in self.ext_modules + self.qext_modules:
            ext.define_macros.append(('KXVER', self.kxver.split('.')[0]))
            ext.define_macros.append(('QVER', self.kxver.split('.')[0]))
            if sys.hexversion >= 0x3000000:
                ext.define_macros.append(('PY3K', "%s%s" % sys.version_info[:2]))
        for exe in self.executables:
            exe.define_macros.append(('QARCH', self.qarch))


###############################################################################

summary, details = __doc__.split('\n\n', 2)
test_requirements = ['pytest>=2.6.4',
                     'pytest-pyq',
                     'pytest-cov>=2.4',
                     'coverage>=4.2']
if sys.version_info[0] < 3:
    test_requirements.append('pathlib2>=2.0')
ipython_requirements = ['ipython']

setup(version=pyq_version,
      distclass=Distribution,
      description=summary,
      long_description=details,
      download_url="https://github.com/enlnt/pyq/archive/pyq-{version}.tar.gz".format(version=pyq_version),
      package_dir={'': 'src'},
      extras_require={
          'test': test_requirements,
          'ipython': ipython_requirements,
          'all': test_requirements + ipython_requirements + [
              'py', 'numpy', 'prompt-toolkit', 'pygments-q'],
      },
      zip_safe=False,
      **metadata)
