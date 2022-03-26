import platform
from pathlib import Path

from setuptools import (find_packages,
                        setup)

import symba

project_base_url = 'https://github.com/lycantropos/symba/'


def read_file(path_string: str) -> str:
    return Path(path_string).read_text(encoding='utf-8')


parameters = dict(
        name=symba.__name__,
        packages=find_packages(exclude=('tests', 'tests.*')),
        version=symba.__version__,
        description=symba.__doc__,
        long_description=read_file('README.md'),
        long_description_content_type='text/markdown',
        author='Azat Ibrakov',
        author_email='azatibrakov@gmail.com',
        license='MIT License',
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
        ],
        url=project_base_url,
        download_url=project_base_url + 'archive/master.zip',
        python_requires='>=3.6',
        install_requires=read_file('requirements.txt'))
if platform.python_implementation() == 'CPython':
    from setuptools import Extension

    parameters.update(
            ext_modules=[Extension('_' + symba.__name__,
                                   ['src/{}.c'.format(symba.__name__)])],
            zip_safe=False
    )
setup(**parameters)
