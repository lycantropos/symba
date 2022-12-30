import platform
from pathlib import Path

from setuptools import (find_packages,
                        setup)

import symba

project_base_url = 'https://github.com/lycantropos/symba/'


def read_file(path_string: str) -> str:
    return Path(path_string).read_text(encoding='utf-8')


package_data = {symba.__name__: ['py.typed']}
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
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
        ],
        url=project_base_url,
        download_url=project_base_url + 'archive/master.zip',
        python_requires='>=3.7',
        install_requires=read_file('requirements.txt')
)
if platform.python_implementation() == 'CPython':
    from glob import glob

    from setuptools import Extension

    extension_module_name = '_' + symba.__name__
    package_data[symba.__name__].append('_symba.pyi')
    parameters.update(ext_modules=[Extension(symba.__name__
                                             + '.' + extension_module_name,
                                             glob('src/*.c'))],
                      zip_safe=False)
parameters['package_data'] = package_data
setup(**parameters)
