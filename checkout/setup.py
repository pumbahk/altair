from setuptools import setup, find_packages

install_requires = [
    "pyramid",
]

tests_require = [
    "nose",
    "coverage",
    "webtest",
]

setup(
    name="altair_checkout",
    package_dir={"": "src"},
    packages=find_packages('src'),
    tests_require=tests_require,
    test_suite="altair_checkout",
    extras_require={
        "testing": tests_require,
        "devtools": ["tox", "sphinx"],
    },
)
