from setuptools import setup

setup(name='imppy',
      version='0.1',
      description='little importer dev tool',
      url='https://github.com/ndufreche/imppy',
      author='Nicolas Dufreche',
      author_email='n.dufreche@gmail.com',
      license='MIT',
      packages=['imppy'],
      scripts=['bin/imppy'],
      install_requires=[
        'MySQL-python',
        'readline',
        'cmd2',
      ],
      zip_safe=False)