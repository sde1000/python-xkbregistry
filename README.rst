xkbregistry
===========

Python bindings for libxkbregistry_ using cffi_.

libxkbregistry_ is part of libxkbcommon_ but is commonly packaged
separately in distributions.

Example usage:

>>> from xkbregistry import rxkb
>>> ctx = rxkb.Context()
>>> ctx.models["pc101"].description
'Generic 101-key PC'
>>> ctx.layouts["us"]
rxkb.Layout('us')
>>> ctx.layouts["us"].description
'English (US)'
>>> ctx.layouts["us(intl)"].description
'English (US, intl., with dead keys)'
>>> ctx.option_groups[0].description
'Switching to another layout'


Version numbering
-----------------

From release 1.0 onwards, the version numbering of this package will
relate to releases of libxkbcommon_ as follows:

If the Python package version is major.minor[.patch] then it requires
at least release major.minor.0 of libxkbcommon and/or libxkbregistry
to build and run, and should work with any subsequent release. The
patch version of the Python package is unrelated to the patch version
of libxkbcommon.

.. _libxkbregistry: https://xkbcommon.org/doc/current/group__registry.html
.. _libxkbcommon: https://xkbcommon.org/
.. _cffi: https://pypi.python.org/pypi/cffi
