import platform

from setuptools import (find_packages,
                        setup)

project_base_url = 'https://github.com/lycantropos/symba/'
parameters = dict(packages=find_packages(exclude=('tests', 'tests.*')),
                  url=project_base_url,
                  download_url=project_base_url + 'archive/master.zip')
if platform.python_implementation() == 'CPython':
    from glob import glob

    from setuptools import Extension

    parameters.update(package_data={'symba': ['_symba.pyi']},
                      ext_modules=[Extension('symba._symba', glob('src/*.c'))],
                      zip_safe=False)
setup(**parameters)
