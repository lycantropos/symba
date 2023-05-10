import platform

from setuptools import (find_packages,
                        setup)

project_base_url = 'https://github.com/lycantropos/symba/'
parameters = dict(packages=find_packages(exclude=('tests', 'tests.*')),
                  package_data={'symba': ['py.typed']},
                  url=project_base_url,
                  download_url=project_base_url + 'archive/master.zip')
if platform.python_implementation() == 'CPython':
    from glob import glob

    from setuptools import Extension
    from setuptools.command.build_ext import build_ext


    class BuildExt(build_ext):
        def build_extensions(self) -> None:
            compile_args = []
            compiler_type = self.compiler.compiler_type
            if compiler_type == 'unix':
                compile_args.append('-Werror')
            elif compiler_type == 'msvc':
                compile_args.append('/WX')
            for extension in self.extensions:
                extension.extra_compile_args += compile_args
            super().build_extensions()


    parameters['package_data']['symba'].append('_symba.pyi')
    parameters.update(cmdclass={build_ext.__name__: BuildExt},
                      ext_modules=[Extension('symba._symba', glob('src/*.c'))],
                      zip_safe=False)
setup(**parameters)
