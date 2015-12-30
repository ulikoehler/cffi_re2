#include <re2/re2.h>
#include <string>
#include <iostream>

using namespace std;

typedef struct {
    bool hasMatch;
    int numGroups;
    char** groups;
} REMatchResult;

/**
 * A multi match object which contains either:
 *  - A list of group matches (individual groups)
 *  - A list of regular matches (one group per match)
 */
typedef struct {
    /**
     * Length of either groupMatches or matches (depending on value of hasGroupMatches)
     */
    int numMatches;
    /**
     * If true, this object contains group matches instead of regular matches.
     */
    bool hasGroupMatches;
    /**
     * Only filled if this result does NOT have group matches (else NULL)
     */
    char** matches;
    /**
     * Only filled if this result has group matches (else NULL)
     */
    char*** groupMatches;
} REMultiMatchResult;

/**
 * Lookup table that maps the Python anchor arg to actual anchors.
 */
static const re2::RE2::Anchor anchorLUT[] = {
    re2::RE2::UNANCHORED, re2::RE2::ANCHOR_BOTH, re2::RE2::ANCHOR_START};

/**
 * Create arg array from StringPiece array.
 * Caller must deallocate args with delete[]
 */
RE2::Arg* stringPiecesToArgs(re2::StringPiece* spc, int n) {
    RE2::Arg* args = new RE2::Arg[n];
    for (int i = 0; i < n; ++i) {
        args[i] = &spc[i];
    }
    return args;
}

/**
 * Copy a StringPiece array to a C string list,
 * each level of which is allocated using new[]
 */
char** copyGroups(const re2::StringPiece* groupsSrc, int numGroups) {
    char** groups = new char*[numGroups];
    for (int i = 0; i < numGroups; ++i) {
        char* group = new char[groupsSrc[i].size() + 1];
        group[groupsSrc[i].size()] = 0; //Insert C terminator
        //Copy actual string
        memcpy(group, groupsSrc[i].data(), groupsSrc[i].size());
        groups[i] = group;
    }
    return groups;
}

extern "C" {
    re2::RE2* RE2_new(const char* pattern) {
        re2::RE2* ptr = new re2::RE2(pattern, re2::RE2::Quiet);
        return ptr;
    }

    int NumCapturingGroups(re2::RE2* re_obj) {
        return re_obj->NumberOfCapturingGroups();
    }

    void FreeREMatchResult(REMatchResult mr) {
        if(mr.groups != 0) {
            for (int i = 0; i < mr.numGroups; ++i) {
                if(mr.groups[i] != 0) {
                    delete[] mr.groups[i];
                }
            }
            delete[] mr.groups;
            mr.groups = 0;
        }
    }

    REMatchResult FindSingleMatch(re2::RE2* re_obj, const char* dataArg, bool fullMatch) {
        re2::StringPiece data(dataArg);
        REMatchResult ret;
        ret.numGroups = re_obj->NumberOfCapturingGroups();
        //Declare group target array
        re2::StringPiece* groups = new re2::StringPiece[ret.numGroups];
        RE2::Arg* args = stringPiecesToArgs(groups, ret.numGroups);
        //Perform either
        if(fullMatch) {
            ret.hasMatch = re2::RE2::FullMatchN(data, *re_obj, &args, ret.numGroups);
        } else {
            ret.hasMatch = re2::RE2::PartialMatchN(data, *re_obj, &args, ret.numGroups);
        }
        //Copy groups
        if(ret.hasMatch) {
            ret.groups = copyGroups(groups, ret.numGroups);
        } else {
            ret.groups = NULL;
        }
        //Cleanup
        delete[] groups;
        delete[] args;
        //Return
        return ret;
    }

    void RE2_delete(re2::RE2* re_obj) {
        delete re_obj;
    }

    string* RE2_GlobalReplace(re2::RE2* re_obj, const char* str, const char* rewrite) {
        string* ptr_s = new string(str);
        re2::StringPiece sp(rewrite);

        re2::RE2::GlobalReplace(ptr_s, *re_obj, sp);
        return ptr_s;
    }

    const char* get_c_str(string* ptr_str) {
        if(ptr_str == NULL) {
            return NULL;
        }
        return ptr_str->c_str();
    }

    void RE2_delete_string_ptr(string* ptr) {
        delete ptr;
    }

    const char* get_error_msg(re2::RE2* re_obj) {
        if(!re_obj) {
            return "";
        }
        string* ptr_s = (string*) &(re_obj->error());
        return get_c_str(ptr_s);
    }
    
    bool ok(re2::RE2* re_obj) {
        if(!re_obj) {
            return false;
        }
        return re_obj->ok();
    }

}
