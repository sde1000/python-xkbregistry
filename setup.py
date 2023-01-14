from setuptools import setup

setup(
    cffi_modules=["xkbregistry/ffi_build.py:ffibuilder"],
)
