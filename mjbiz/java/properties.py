#!/usr/bin/env python3
"""
My Module
"""

import io
import logging


_log = logging.getLogger(__name__)
logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)

INITIAL = 1
COMMENT = 2
TOKEN_NAME = 3
TOKEN_SEPARATION = 4
TOKEN_VALUE = 5


WHITESPACE = (b' ', b'\t', b'\r')
COMMENT_START = (b'#', b'!')


class PropertyParser:

    def __init__(self, stream):
        self.stream = stream
        self.context = INITIAL

    def next(self):
        c = self.stream.read(1)
        return c

    def register_token_value(self, props, token, value=b''):
        _log.debug('{token} = {value}'.format(token=token, value=value))
        props[token.decode('unicode_escape')] = value.decode('unicode_escape')

    def parse(self, p):
        token = io.BytesIO()
        value = io.BytesIO()
        while True:
            c = self.next()
            _log.debug(repr('{ctx}:{c}:'.format(ctx=self.context, c=c)))
            if self.context == COMMENT:
                if c == b'\n':
                    self.context = INITIAL
                elif c == b'':
                    return
                continue

            if self.context == INITIAL:
                if c in WHITESPACE:
                    # We skip whitespace
                    pass
                elif c == b'\n':
                    pass
                elif c in COMMENT_START:
                    self.context = COMMENT
                elif c == b'':
                    return
                else:
                    self.context = TOKEN_NAME

            if self.context == TOKEN_NAME:
                if c == b'\\':
                    c = self.next()
                    if c == b'r':
                        token.write(br'\r')
                    elif c == b'n':
                        token.write(br'\n')
                    elif c == b'u':
                        token.write(br'\u')
                    elif c == b'\\':
                        token.write(br'\\')
                    else:
                        token.write(c)
                elif c in WHITESPACE:
                    self.context = TOKEN_SEPARATION
                elif c in (b':', b'=', b''):
                    self.context = TOKEN_SEPARATION
                elif c in (b'\n',):
                    self.register_token_value(p, token.getvalue())
                    token = io.BytesIO()
                    value = io.BytesIO()
                    self.context = INITIAL
                else:
                    token.write(c)
                continue

            if self.context == TOKEN_SEPARATION:
                if c in WHITESPACE or c in (b':', b'='):
                    continue
                else:
                    self.context = TOKEN_VALUE
                # FALL THROUGH

            if self.context == TOKEN_VALUE:
                if c == b'\\':
                    c = self.next()
                    if c == b'r':
                        value.write(br'\r')
                    elif c == b'n':
                        value.write(br'\n')
                    elif c == b'u':
                        value.write(br'\u')
                    elif c == b'\\':
                        value.write(br'\\')
                    elif c == b'\n':
                        self.context = TOKEN_SEPARATION
                    else:
                        value.write(c)
                else:
                    if c in (b'\n', b''):
                        self.register_token_value(
                            p,
                            token.getvalue(),
                            value.getvalue())
                        token = io.BytesIO()
                        value = io.BytesIO()
                        self.context = INITIAL
                    else:
                        value.write(c)
                    if c == b'':
                        return
                continue


class Properties:
    r"""
    This class implements a simple Java like property file format.

    The format is described in the Java documentation under
    `java.util.Properties#load()`_ and on the `.properties wikipedia entry`_.

    Each line in a properties file stores a single property. A property can be
    defined with three different syntaxes:

    1. ``name = Michael Jansen``
    2. ``email: info@michael-jansen.biz``
    3. ``homepage http://michael-jansen.biz``

    Lines starting with either ``#`` or ``!`` as the first non blank character
    are considered comments.

    The file encoding is latin-1 and its possible to use unicode escape
    sequences.

    Lines ending in a backslash ``\`` will continue on the next line. Leading
    spaces are always discarded. Trailing spaces kept.

    >>> txt = '''
    ... # This is a comment
    ... java.home = /opt/java/1.6
    ...   ! This is a comment too.
    ... java.args :    -Xms=512m -Xmx=512m
    ... install.root   /opt\\
    ...                /ddd
    ... weird\:properties can be used too.
    ... msg = \\u0e4f
    ... '''
    >>> p = Properties()
    >>> p.parse(txt.encode('latin-1'))
    >>> print(str(p))
    install.root = /opt/ddd
    java.args = -Xms=512m -Xmx=512m
    java.home = /opt/java/1.6
    msg = \u0e4f
    weird\:properties = can be used too.
    >>> print(repr(p))
    install.root = /opt/ddd
    java.args = -Xms=512m -Xmx=512m
    java.home = /opt/java/1.6
    msg = ๏
    weird\:properties = can be used too.
    >>> print(p['msg'])
    ๏

    .. _.properties wikipedia entry: http://en.wikipedia.org/wiki/.properties
    .. _java.util.Properties#load(): http://docs.oracle.com/javase/7/docs/api/java/util/Properties.html#load(java.io.Reader)
    """

    def __init__(self):
        self.__properties = dict()

    def __len__(self):
        return len(self.__properties)

    def __getitem__(self, token):
        if isinstance(token, slice):
            raise TypeError('slice not supported')
        else:
            return self.__properties[token]

    def keys(self):
        return self.__properties.keys()

    __iter__ = keys

    def parse(self, txt):
        if isinstance(txt, str):
            stream = io.BytesIO(txt)
        elif isinstance(txt, bytes):
            stream = io.BytesIO(txt)
        else:
            stream = txt
        p = PropertyParser(stream)
        p.parse(self)

    def __contains__(self, token):
        return token in self.__properties

    def __setitem__(self, token, value):
        if isinstance(token, slice):
            raise TypeError('slice not supported')
        else:
            self.__properties[token] = value

    def __delitem__(self, token, value):
        if isinstance(token, slice):
            raise TypeError('slice not supported')
        else:
            del self.__properties[token]

    def _escape(self, s):
        if isinstance(s, bytes):
            return s.replace(b':', b'\:').replace(b' ', br'\ ')
        else:
            return s.replace(':', '\:').replace(' ', r'\ ')

    def __str__(self):
        l = []
        for k, v in sorted(self.__properties.items()):
            k=self._escape(k.encode('unicode_escape'))
            v=v.encode('unicode_escape')
            l.append(k + b" = " + v)
        return b'\n'.join(l).decode('latin-1')

    def __repr__(self):
        l = []
        for k, v in sorted(self.__properties.items()):
            l.append('{k} = {v}'.format(
                k=self._escape(k),
                v=v))
        return '\n'.join(l)


def main(args):
    import doctest
    return doctest.testmod()


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
