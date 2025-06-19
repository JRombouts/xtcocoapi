from setuptools import setup, Extension

def get_numpy_include():
    """Defer numpy import until build time"""
    try:
        import numpy as np
        return np.get_include()
    except ImportError:
        return None

version_file = 'xtcocotools/version.py'

def get_version():
    with open(version_file, 'r') as f:
        exec(compile(f.read(), version_file, 'exec'))
    import sys
    # return short version for sdist
    if 'sdist' in sys.argv or 'bdist_wheel' in sys.argv:
        return locals()['short_version']
    else:
        return locals()['__version__']

def parse_requirements(fname='requirements.txt', with_version=True):
    """Parse the package dependencies listed in a requirements file but strips
    specific versioning information.

    Args:
        fname (str): path to requirements file
        with_version (bool, default=False): if True include version specs

    Returns:
        List[str]: list of requirements items

    CommandLine:
        python -c "import setup; print(setup.parse_requirements())"
    """
    import sys
    from os.path import exists
    import re
    require_fpath = fname

    def parse_line(line):
        """Parse information from a line in a requirements text file."""
        if line.startswith('-r '):
            # Allow specifying requirements in other files
            target = line.split(' ')[1]
            for info in parse_require_file(target):
                yield info
        else:
            info = {'line': line}
            if line.startswith('-e '):
                info['package'] = line.split('#egg=')[1]
            elif '@git+' in line:
                info['package'] = line
            else:
                # Remove versioning from the package
                pat = '(' + '|'.join(['>=', '==', '>']) + ')'
                parts = re.split(pat, line, maxsplit=1)
                parts = [p.strip() for p in parts]

                info['package'] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    if ';' in rest:
                        # Handle platform specific dependencies
                        # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                        version, platform_deps = map(str.strip,
                                                     rest.split(';'))
                        info['platform_deps'] = platform_deps
                    else:
                        version = rest  # NOQA
                    info['version'] = (op, version)
            yield info

    def parse_require_file(fpath):
        with open(fpath, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    for info in parse_line(line):
                        yield info

    def gen_packages_items():
        if exists(require_fpath):
            for info in parse_require_file(require_fpath):
                parts = [info['package']]
                if with_version and 'version' in info:
                    parts.extend(info['version'])
                if not sys.version.startswith('3.4'):
                    # apparently package_deps are broken in 3.4
                    platform_deps = info.get('platform_deps')
                    if platform_deps is not None:
                        parts.append(';' + platform_deps)
                item = ''.join(parts)
                yield item

    packages = list(gen_packages_items())
    return packages

# To compile and install locally run "python setup.py build_ext --inplace"
# To install library to Python site-packages run "python setup.py build_ext install"
# Note that the original compile flags below are GCC flags unsupported by the Visual C++ 2015 build tools.
# They can safely be removed.
def get_ext_modules():
    """Build extension modules with proper numpy include handling"""
    numpy_include = get_numpy_include()
    include_dirs = ['./common']
    if numpy_include:
        include_dirs.append(numpy_include)
    
    return [
        Extension(
            'xtcocotools._mask',
            sources=['./common/maskApi.c', 'xtcocotools/_mask.pyx'],
            include_dirs=include_dirs,
            extra_compile_args=[] # originally was ['-Wno-cpp', '-Wno-unused-function', '-std=c99'],
        )
    ]

setup(
    name='xtcocotools',
    packages=['xtcocotools'],
    package_dir = {'xtcocotools': 'xtcocotools'},
    install_requires=parse_requirements('requirements.txt'),
    setup_requires=[
        'setuptools>=18.0',
        'cython>=0.27.3',
        'numpy>=1.15.0; python_version=="3.6"',
        'numpy>=1.16.0; python_version=="3.7"',
        'numpy>=1.19.0; python_version=="3.8"',
        'numpy>=1.21.0; python_version=="3.9"',
        'numpy>=1.23.0; python_version=="3.10"',
        'numpy>=1.25.0; python_version=="3.11"',
        'numpy>=2.0.0; python_version>="3.12"'
    ],
    version=get_version(),
    description="Extended COCO API",
    url="https://github.com/jin-s13/xtcocoapi",
    ext_modules=get_ext_modules(),
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
