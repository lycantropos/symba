import platform
from pathlib import Path

from setuptools import (find_packages,
                        setup)

project_base_url = 'https://github.com/lycantropos/symba/'


def read_file(path_string: str) -> str:
    return Path(path_string).read_text(encoding='utf-8')


package_data = {'symba': ['py.typed']}
parameters = dict(packages=find_packages(exclude=('tests', 'tests.*')),
                  url=project_base_url,
                  download_url=project_base_url + 'archive/master.zip')
if platform.python_implementation() == 'CPython':
    from glob import glob

    from setuptools import Extension

    package_data['symba'].append('_symba.pyi')
    parameters.update(ext_modules=[Extension('symba._symba', glob('src/*.c'))],
                      zip_safe=False)
parameters['package_data'] = package_data
setup(**parameters)
