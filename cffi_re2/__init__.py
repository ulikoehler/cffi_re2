#!/usr/bin/env python
#encoding=utf-8
import cffi
import imp

import pkg_resources
import os
import re
import six
from _cffi_re2 import ffi
from _cffi_re2 import lib as libre2

with open("foo.txt","w") as of:
    of.write(str(libre2.__dict__))

#dirname = os.path.abspath(os.path.join(dirname, '..'))
#import glob
#search_string = os.path.join(dirname, '_cre2*.so')
#flist = glob.glob(search_string)
#
#libre2 = None
#if flist:
#    soname = flist[0]
#

#ffi = cffi.FFI()
#libre2 = ffi.dlopen(soname)

class MatchObject(object):
    def __init__(self, re, groups):
        self.re = re
        self._groups = groups
    def group(self, i):
        return self._groups[i]
    def groups(self):
        return self._groups
    def __str__(self):
        return "MatchObject(groups={0})".format(self._groups)

RE_COM = re.compile('\(\?\#.*?\)')  

class CRE2:
    def __init__(self, pattern, *args, **kwargs):
        pattern = CRE2.__convertToBinaryUTF8(pattern)
        self.pattern = pattern

        if 'compat_comment' in kwargs:
            pattern = RE_COM.sub('', pattern)

        self.re2_obj = ffi.gc(libre2.RE2_new(pattern), libre2.RE2_delete)
        flag = libre2.ok(self.re2_obj)
        if not flag:
            ret = libre2.get_error_msg(self.re2_obj)
            raise ValueError(ffi.string(ret))

        self.libre2 = libre2

    @staticmethod
    def __convertToBinaryUTF8(data):
        if isinstance(data, six.text_type):
            return data.encode("utf-8")
        return data

    def search(self, data, flags=0):
        return self.__search(data, False)  # 0 => UNANCHORED

    def match(self, data, flags=0):
        return self.__search(data, True)  # 0 => ANCHOR_BOTH

    def __search(self, data, fullMatch=False):
        """
        Search impl that can either be performed in full or partial match
        mode, depending on the anchor argument
        """
        # RE2 needs binary data, so we'll need to encode it
        data = CRE2.__convertToBinaryUTF8(data)

        if isinstance(data, six.text_type):
            data = data.encode("utf-8")

        matchobj = libre2.FindSingleMatch(self.re2_obj, data, fullMatch)
        if matchobj.hasMatch:
            # Capture groups
            groups = [ffi.string(matchobj.groups[i]).decode("utf-8")
                      for i in range(matchobj.numGroups)]
            ret = MatchObject(self, groups)
        else:
            ret = None
        # Cleanup C API objects
        libre2.FreeREMatchResult(matchobj)
        return ret

    def findall(self, data, flags=0):
        return list(self.finditer(data, flags))

    def finditer(self, data, flags=0):
        data = CRE2.__convertToBinaryUTF8(data)

        # Anchor currently fixed to 0 == UNANCHORED
        matchobj = libre2.FindAllMatches(self.re2_obj, data, 0)

        for tp in CRE2.__parseFindallMatchObj(matchobj):
            if len(tp) == 1:  # No groups, onlyf full match:
                yield tp[0]
            else:
                yield tp

        libre2.FreeREMultiMatchResult(matchobj)

    @staticmethod
    def __parseFindallMatchObj(matchobj):
        # Define
        n = matchobj.numMatches
        m = matchobj.numGroups
        # Iterate
        for i in range(n):
            yield tuple(ffi.string(matchobj.groupMatches[i][j]).decode("utf-8") for j in range(m))

    def sub(self, repl, s, count=0):
        # Convert all strings to UTF8
        repl = CRE2.__convertToBinaryUTF8(repl)
        s = CRE2.__convertToBinaryUTF8(s)

        c_p_str = self.libre2.RE2_GlobalReplace(self.re2_obj, s, repl)

        py_string = ffi.string(self.libre2.get_c_str(c_p_str))
        # Cleanup C API objects
        self.libre2.RE2_delete_string_ptr(c_p_str)
        return py_string.decode("utf-8")

def compile(pattern, *args, **kwargs):
    return CRE2(pattern, *args, **kwargs)
