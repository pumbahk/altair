from setuptools import setup, find_packages


setup(name="altair.request",
      install_requires=[
          "setuptools>0.7",
          "pyramid",
          "webob",
      ],
      packages=find_packages("src"),
      namespace_packages=["altair"],
      package_dir={"": "src"},
)
