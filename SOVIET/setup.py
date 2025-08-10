# setup.py
from setuptools import setup, find_packages

setup(
    name='sovietcy',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'scapy',
        'rich',
        'textual',
        'Flask',  # For the phishing server
        'requests', # For cloning websites
        # Add any other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'sovietcy=sovietcy.main:run_sovietcy',
        ],
    },
    author='RAKEGPT', # Or your preferred identity
    description='A highly dangerous network analysis and phishing toolkit.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo/sovietcy', # Change this if you want to host it
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Or choose a more restrictive one
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
