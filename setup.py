from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(name='pytaringa',
      version='0.1.4',
      author='OverJT',
      author_email='me@over.cf',
      license='MIT',
      description='Un wrapper de taringa',
      long_description=readme,
      install_requires=[
        "requests",
      ],
      packages=find_packages())
