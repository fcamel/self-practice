#!/usr/bin/env python
# -*- encoding: utf8 -*-

import unittest
import tempfile
import os

import my_file

class FileWithoutBeginningBytesTest(unittest.TestCase):
    def setUp(self):
        self.file_object = tempfile.NamedTemporaryFile(
            prefix='test_', delete=False)
        self.content = '0123456789'
        self.file_object.write(self.content)
        self.file_object.close()
        self.file_path = self.file_object.name
        self.file_object = open(self.file_path)

    def tearDown(self):
        self.file_object.close()
        os.remove(self.file_path)

    def testNoDropBeginningBytes(self):
        actual = my_file.FileWithoutBeginningBytes(self.file_object, 0)
        self.assertEquals(self.content, actual.read())

        actual.seek(0)
        self.assertEquals(0, actual.tell())
        self.assertEquals(self.content, actual.read())

        actual.seek(0, 2)
        self.assertEquals(len(self.content), actual.tell())

        actual.seek(-3, 1)
        self.assertEquals(len(self.content) - 3, actual.tell())

        actual.seek(1, 1)
        self.assertEquals(len(self.content) - 2, actual.tell())

    def testDropBeginningBytes(self):
        begin_offset = 3
        actual = my_file.FileWithoutBeginningBytes(self.file_object,
                                                   begin_offset)
        # Note that the beginning bytes should not be read
        # after the object is created.
        self.assertEquals(self.content[begin_offset:], actual.read())

        actual.seek(0)
        self.assertEquals(0, actual.tell())
        self.assertEquals(self.content[begin_offset:], actual.read())


        actual.seek(0, 2)
        self.assertEquals(len(self.content) - begin_offset, actual.tell())

        actual.seek(-3, 1)
        self.assertEquals(len(self.content) - begin_offset - 3, actual.tell())

        actual.seek(1, 1)
        self.assertEquals(len(self.content) - begin_offset - 2, actual.tell())

    def testNone(self):
        actual = my_file.FileWithoutBeginningBytes(None, 0)
        with self.assertRaises(AttributeError):
            actual.read()

        with self.assertRaises(AttributeError):
            actual.seek(0)

        with self.assertRaises(AttributeError):
            actual.tell()


if __name__ == '__main__':
    unittest.main()
