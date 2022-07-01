from setuptools import setup, find_packages
import coppertop.core

# read the contents of README.md file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

version = coppertop.core.version

# print(find_packages())


setup(
  name='coppertop-bones',
  packages=[
    'bones',
    'bones.core',
    'bones.core.tests',
    'bones.kernel',
    'bones.kernel.tests',
    'bones.lang',
    'bones.lang.tests',
    'bones.lang.tests.bones',
    'bones.libs',
    'bones.libs.on_demand',
    'bones.tests',
    'bones.tour',
    'coppertop',
    'coppertop.examples',
    'coppertop.tests',
  ],
  # package_dir = {'': 'core'},
  # namespace_packages=['coppertop_'],
  version=version,
  python_requires='>=3.8',
  license='AGPLv3',
  description = 'Some batteries Python didn\'t come with',
  long_description_content_type='text/markdown',
  long_description=long_description,
  author = 'David Briant',
  author_email = 'dangermouseb@forwarding.cc',
  url = 'https://github.com/DangerMouseB/coppertop-bones',
  download_url = '',
  # download_url = f'https://github.com/DangerMouseB/coppertop/archive/{version}.tar.gz',
  keywords = ['piping', 'pipeline', 'pipe', 'functional'],
  install_requires=[],
  include_package_data=True,
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'Topic :: Utilities',
    'License :: OSI Approved :: GNU Affero General Public License v3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
  zip_safe=False,
)

# https://autopilot-docs.readthedocs.io/en/latest/license_list.html
