#!/usr/bin/env python
#encoding=utf-8

__version__ = '0.1.4'

import cffi
import imp

import pkg_resources
import os
import re
import six

dirname = pkg_resources.resource_filename('cffi_re2', '')
dirname = os.path.abspath(os.path.join(dirname, '..'))
import glob
search_string = os.path.join(dirname, '_cre2*.so')
flist = glob.glob(search_string)

libre2 = None
if flist:
    soname = flist[0]
    ffi = cffi.FFI()

    ffi.cdef('''
    typedef struct {
        bool hasMatch;
        int numGroups;
        char** groups;
    } REMatchResult;

    void FreeREMatchResult(REMatchResult mr);

    void* RE2_new(const char* pattern);
    REMatchResult FindSingleMatch(void* re_obj, const char* data, bool fullMatch);
    void RE2_delete(void* re_obj);
    void RE2_delete_string_ptr(void* ptr);
    void* RE2_GlobalReplace(void* re_obj, const char* str, const char* rewrite);
    const char* get_c_str(void* ptr_str);
    const char* get_error_msg(void* re_obj);
    bool ok(void* re_obj);
    ''')

    libre2 = ffi.dlopen(soname)


def force_str(s):
    if isinstance(s, six.text_type):
        return s.encode('utf-8')
    return str(s)

class MatchObject(object):
    def __init__(self, re, groups):
        self.re = re
        self.groups = groups
    def group(self, i):
        return self.groups[i]

RE_COM = re.compile('\(\?\#.*?\)')  

class CRE2:
    def __init__(self, pattern, *args, **kwargs):
        self.pattern = pattern = force_str(pattern)

        if 'compat_comment' in kwargs:
            pattern = RE_COM.sub('', pattern)

        self.re2_obj = ffi.gc(libre2.RE2_new(pattern), libre2.RE2_delete)
        flag = libre2.ok(self.re2_obj)
        if not flag:
            ret = libre2.get_error_msg(self.re2_obj)
            raise ValueError(ffi.string(ret))

        self.libre2 = libre2

    def match(self, data):
        """
        Perform a full regex match on the given data string
        """
        if isinstance(data, six.text_type):
            data = data.encode("utf-8")

    def search(self, data):
        return self.__search(data, False) # 0 => UNANCHORED

    def match(self, data):
        return self.__search(data, True) # 0 => ANCHOR_BOTH

    def __search(self, data, fullMatch=False):
        """
        Search impl that can either be performed in full or partial match
        mode, depending on the anchor argument
        """
        # RE2 needs binary data, so we'll need to encode it
        if isinstance(data, six.text_type):
            data = data.encode("utf-8")

        matchobj = libre2.FindSingleMatch(self.re2_obj, data, fullMatch)
        print(matchobj)
        print(matchobj.hasMatch)
        if matchobj.hasMatch:
            # Capture groups
            groups = [matchobj.groups[i] for i in range(matchobj.numGroups)]
            return MatchObject(self, groups)
        # else: return None

    def sub(self, repl, str, count=0):
        c_p_str = self.libre2.RE2_GlobalReplace(self.re2_obj, str, repl)

        py_string = ffi.string(self.libre2.get_c_str(c_p_str))
        self.libre2.RE2_delete_string_ptr(c_p_str)
        return py_string

def compile(pattern, *args, **kwargs):
    return CRE2(pattern, *args, **kwargs)
