#!/usr/bin/env python3
"""
"""
import mjbiz.java.properties

import doctest
import sys
import textwrap
import unittest


class MyProperties(mjbiz.java.properties.Properties):
    """Wrapper class for Properties that encodes a string to latin-1."""
    def parse(self, txt):
        super().parse(txt.encode('latin-1'))


class MyPropertiesTest(unittest.TestCase):
    """
    Unit tests for class `MyProperties`.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hash_comments(self):
        """Check that comments starting with hash (#) are supported."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            # This is a comment
            token.a = 1
            # This is a comment
            token.b = 2
            # This is a comment
            '''))
        self.assertEqual(len(p), 2)

    def test_bang_comments(self):
        """Check that comments starting with bang (!) are supported."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            ! This is a comment
            token.a = 1
            ! This is a comment
            token.b = 2
            ! This is a comment
            '''))
        self.assertEqual(len(p), 2)

    def test_equal_assignment_works(self):
        """Check that propery declaration using equal (=) works."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            token.a=1
            token.b = 2
            '''))
        self.assertEqual(p['token.a'], '1')
        self.assertEqual(p['token.b'], '2')

    def test_colon_assignment_works(self):
        """Check that propery declaration using color (:) works."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            token.a:1
            token.b : 2
            '''))
        self.assertEqual(p['token.a'], '1')
        self.assertEqual(p['token.b'], '2')

    def test_space_assignment_works(self):
        """Check that propery declaration using space ( ) works."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            token.a 1
            token.b    2
            token.c
            '''))
        self.assertEqual(p['token.a'], '1')
        self.assertEqual(p['token.b'], '2')
        self.assertEqual(p['token.c'], '')

    def test_line_continuation_works(self):
        """Check that line continuation works."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            # Rules:
            #   - Line continuation disregards leading whitespace on
            #     continuation lines.
            #   - But not those before the continuation
            token.a = This is a long \
                    token value  \\\
             over 3 lines
            token.b 2
            '''))
        self.assertEqual(
            p['token.a'],
            r'This is a long token value  \over 3 lines')
        self.assertEqual(p['token.b'], '2')

    def test_comment_continuation_does_not_work(self):
        """Make sure comment lines do not support continuation."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            # This is a very long comment that should not \
            continue on this line
            '''))
        self.assertIn('continue', p)

    def test_escaping_works(self):
        """Make sure the escape rules are heeded."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            # The next line is not a continuation
            token.a = my value \\
            # The colon on the next line does not end the token name
            token\:a = token:a
            # Then whitespaces in the next line are ignored. The escaping to
            token.b =      \a\b\c\d\e
            token\\c = val
            token\ d allowed
            token\rd allowe\rd
            token\nd allowe\nd
            \:\= valid too
            '''))
        self.assertEqual(p['token.a'], 'my value \\')
        self.assertEqual(p['token:a'], 'token:a')
        self.assertEqual(p['token.b'], 'abcde')
        self.assertEqual(p['token\\c'], 'val')
        self.assertEqual(p['token d'], 'allowed')
        self.assertEqual(p['token\rd'], 'allowe\rd')
        self.assertEqual(p['token\nd'], 'allowe\nd')
        self.assertEqual(p[':='], 'valid too')

    def test_unicode_handling(self):
        """Make sure the unicode handling works."""
        p = MyProperties()
        p.parse(textwrap.dedent(r'''
            # Not a valid unicode string (double backslash)
            token.a = \\u0e4f\\u032f\\u0361\\u0e4f
            # A valid unicode string
            token.b = \u0e4f\u032f\u0361\u0e4f
            token.c = \u0e4f
            '''))
        self.assertEqual(p['token.a'], r'\u0e4f\u032f\u0361\u0e4f')
        self.assertEqual(p['token.b'], '๏̯͡๏')
        self.assertEqual(p['token.c'], '๏')

    def test_unicode_errors(self):
        """Make sure the unicode handling works."""
        p = MyProperties()
        self.assertRaises(
            UnicodeDecodeError,
            p.parse,
            textwrap.dedent(r'''
                # Not a valid unicode string. To short
                token.a = \u0e
                '''))

    def test_doctest(self):
        # import doctest
        # doctest.testmod()
        pass


if __name__ == '__main__':
    sys.exit(unittest.main())
