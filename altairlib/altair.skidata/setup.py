import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="altair.skidata",
    version="0.0.0",
    author="",
    author_email="",
    description="SOAP API Client for SKIDATA",
    long_description=long_description,
    url="https://github.com/ticketstar/altair",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['altair'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools', 'enum34',  'lxml'],
    test_requires=['nose'],
    test_suite='altair.skidata',
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
