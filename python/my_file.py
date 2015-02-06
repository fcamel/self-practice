#!/usr/bin/env python
# -*- encoding: utf8 -*-

class FileWithoutBeginningBytes(object):
    '''
    The proxy of the built-in file object.

    The only difference is that we override seek() and tell() to ensure that
    some beginning bytes are not read.
    '''
    def __init__(self, file_object, begin_offset):
        # file_object may be None or any file-like object.
        if file_object is None:
            self._file_object = None
            self._begin_offset = 0
        else:
            self._file_object = file_object
            self._begin_offset = begin_offset
            self.seek(0)

    def seek(self, offset, whence=0):
        if self._file_object is None:
            msg = "'NoneType' object has no attribute 'seek'"
            raise AttributeError(msg)
        if whence == 0:
            # From begin. Add the offset.
            offset += self._begin_offset
        else:
            # From current or the end. No need to modify.
            pass
        self._file_object.seek(offset, whence)

    def tell(self):
        if self._file_object is None:
            msg = "'NoneType' object has no attribute 'tell'"
            raise AttributeError(msg)
        # Always subtracting the offset to return the correct value.
        result = self._file_object.tell() - self._begin_offset
        return result

    def __str__(self):
        return 'FileWithoutBeginningBytes' + str(self._file_object)

    def __getattr__(self, attr):
        if self._file_object is None:
            msg = "'NoneType' object has no attribute '%s'" % attr
            raise AttributeError(msg)
        return getattr(self._file_object, attr)
