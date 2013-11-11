"""This module contains general utility code that is used throughout
the library.

For users of this library, the C{L{log}} function is probably the most
interesting.
"""

__all__ = ['log', 'appendArgs', 'toBase64', 'fromBase64', 'autoSubmitHTML']

import binascii
import sys
import urlparse

from urllib import urlencode

elementtree_modules = [
    'lxml.etree',
    'xml.etree.cElementTree',
    'xml.etree.ElementTree',
    'cElementTree',
    'elementtree.ElementTree',
    ]

def autoSubmitHTML(form, title='OpenID transaction in progress'):
    return """
<html>
<head>
  <title>%s</title>
</head>
<body onload="document.forms[0].submit();">
%s
<script>
var elements = document.forms[0].elements;
for (var i = 0; i < elements.length; i++) {
  elements[i].style.display = "none";
}
</script>
</body>
</html>
""" % (title, form)

def importElementTree(module_names=None):
    """Find a working ElementTree implementation, trying the standard
    places that such a thing might show up.

    >>> ElementTree = importElementTree()

    @param module_names: The names of modules to try to use as
        ElementTree. Defaults to C{L{elementtree_modules}}

    @returns: An ElementTree module
    """
    if module_names is None:
        module_names = elementtree_modules

    for mod_name in module_names:
        try:
            ElementTree = __import__(mod_name, None, None, ['unused'])
        except ImportError:
            pass
        else:
            # Make sure it can actually parse XML
            try:
                ElementTree.XML('<unused/>')
            except (SystemExit, MemoryError, AssertionError):
                raise
            except:
                why = sys.exc_info()[1]
                log('Not using ElementTree library %r because it failed to '
                    'parse a trivial document: %s' % (mod_name, why))
            else:
                return ElementTree
    else:
        raise ImportError('No ElementTree library found. '
                          'You may need to install one. '
                          'Tried importing %r' % (module_names,)
                          )

def log(message, level=0):
    """Handle a log message from the OpenID library.

    This implementation writes the string it to C{sys.stderr},
    followed by a newline.

    Currently, the library does not use the second parameter to this
    function, but that may change in the future.

    To install your own logging hook::

      from openid import oidutil

      def myLoggingFunction(message, level):
          ...

      oidutil.log = myLoggingFunction

    @param message: A string containing a debugging message from the
        OpenID library
    @type message: str

    @param level: The severity of the log message. This parameter is
        currently unused, but in the future, the library may indicate
        more important information with a higher level value.
    @type level: int or None

    @returns: Nothing.
    """

    sys.stderr.write(message)
    sys.stderr.write('\n')

def appendArgs(url, args):
    """Append query arguments to a HTTP(s) URL. If the URL already has
    query arguemtns, these arguments will be added, and the existing
    arguments will be preserved. Duplicate arguments will not be
    detected or collapsed (both will appear in the output).

    @param url: The url to which the arguments will be appended
    @type url: str

    @param args: The query arguments to add to the URL. If a
        dictionary is passed, the items will be sorted before
        appending them to the URL. If a sequence of pairs is passed,
        the order of the sequence will be preserved.
    @type args: A dictionary from string to string, or a sequence of
        pairs of strings.

    @returns: The URL with the parameters added
    @rtype: str
    """
    if hasattr(args, 'items'):
        args = args.items()
        args.sort()
    else:
        args = list(args)

    if len(args) == 0:
        return url

    if '?' in url:
        sep = '&'
    else:
        sep = '?'

    # Map unicode to UTF-8 if present. Do not make any assumptions
    # about the encodings of plain bytes (str).
    i = 0
    for k, v in args:
        if type(k) is not str:
            k = k.encode('UTF-8')

        if type(v) is not str:
            v = v.encode('UTF-8')

        args[i] = (k, v)
        i += 1

    return '%s%s%s' % (url, sep, urlencode(args))

def toBase64(s):
    """Represent string s as base64, omitting newlines"""
    return binascii.b2a_base64(s)[:-1]

def fromBase64(s):
    try:
        return binascii.a2b_base64(s)
    except binascii.Error, why:
        # Convert to a common exception type
        raise ValueError(why[0])

class Symbol(object):
    """This class implements an object that compares equal to others
    of the same type that have the same name. These are distict from
    str or unicode objects.
    """

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.__class__, self.name))
   
    def __repr__(self):
        return '<Symbol %s>' % (self.name,)
