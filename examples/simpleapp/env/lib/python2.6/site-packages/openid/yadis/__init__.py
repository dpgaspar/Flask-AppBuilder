

__all__ = [
    'constants',
    'discover',
    'etxrd',
    'filters',
    'manager',
    'parsehtml',
    'services',
    'xri',
    'xrires',
    ]

__version__ = '[library version:1.1.0-rc1]'[17:-1]

# Parse the version info
try:
    version_info = map(int, __version__.split('.'))
except ValueError:
    version_info = (None, None, None)
else:
    if len(version_info) != 3:
        version_info = (None, None, None)
    else:
        version_info = tuple(version_info)
