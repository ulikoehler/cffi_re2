#!/usr/bin/env python
from cffi import FFI
ffi = FFI()


ffi.cdef('''
    typedef struct {
        bool hasMatch;
        int numGroups;
        char** groups;
    } REMatchResult;

    typedef struct {
        int numMatches;
        int numGroups;
        char*** groupMatches;
    } REMultiMatchResult;

    void FreeREMatchResult(REMatchResult* mr);
    void FreeREMultiMatchResult(REMultiMatchResult* mr);

    void* RE2_new(const char* pattern);
    REMatchResult FindSingleMatch(void* re_obj, const char* data, bool fullMatch);
    REMultiMatchResult FindAllMatches(void* re_obj, const char* data, int anchorArg);
    void RE2_delete(void* re_obj);
    void RE2_delete_string_ptr(void* ptr);
    void* RE2_GlobalReplace(void* re_obj, const char* str, const char* rewrite);
    const char* get_c_str(void* ptr_str);
    const char* get_error_msg(void* re_obj);
    bool ok(void* re_obj);
''')
with open("_cre2.cpp") as infile:
    ffi.set_source("_cffi_re2", "", sources=["_cre2.cpp"], source_extension='.cpp', libraries=["re2"])


if __name__ == "__main__":
    ffi.compile()