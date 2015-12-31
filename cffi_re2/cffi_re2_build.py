#!/usr/bin/env python
from cffi import FFI
ffi = FFI()

#ffi.cdef("""void* RE2_new(const char* pattern);""")

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

    void FreeREMatchResult(REMatchResult mr);
    void FreeREMultiMatchResult(REMultiMatchResult mr);

    RE2* RE2_new(const char* pattern);
    REMatchResult FindSingleMatch(RE2* re_obj, const char* data, bool fullMatch);
    REMultiMatchResult FindAllMatches(RE2* re_obj, const char* data, int anchorArg);
    void RE2_delete(RE2* re_obj);
    void RE2_delete_string_ptr(RE2* ptr);
    RE2* RE2_GlobalReplace(RE2* re_obj, const char* str, const char* rewrite);
    const char* get_c_str(RE2* ptr_str);
    const char* get_error_msg(RE2* re_obj);
    bool ok(RE2* re_obj);
''')
ffi.set_source("_cffi_re2", None)

if __name__ == "__main__":
    ffi.compile()