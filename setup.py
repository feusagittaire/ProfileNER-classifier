from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Science/Research',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='ProfileNER-classifier',
  version='0.7.5',
  description="Performs Classification using Regex for social media user's profile categorization and NER tasks",
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description_content_type='text/markdown',
  url='',  
  author='Arthur Lopes',
  author_email='arthurdslopes@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['NER', 'profile categories','classification','social media'],
  packages=find_packages(),
  install_requires=[''],
  include_package_data=True
)