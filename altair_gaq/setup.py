from setuptools import setup, find_packages

setup(name="altair_gaq",
    install_requires=[
        "pyramid",
        "fanstatic",
    ],

    entry_points="""
    [fanstatic.libraries]
    altair_gaq=altair_gaq.fanstatic_resources:altair_gaq
    """
)
