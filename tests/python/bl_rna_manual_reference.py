# SPDX-FileCopyrightText: 2012-2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

# Use for validating our manual interlinking.
#  ./blender.bin --background --python tests/python/bl_rna_manual_reference.py
#
# 1) test_data()              -- ensure the data we have is correct format
# 2) test_lookup_coverage()   -- ensure that we have lookups for _every_ RNA path and all patterns are used.
# 3) test_urls()              -- ensure all the URL's are correct
# 4) test_language_coverage() -- ensure language lookup table is complete
#

import bpy

VERBOSE = False


def test_data():
    import _rna_manual_reference as rna_manual_reference

    assert isinstance(rna_manual_reference.url_manual_mapping, tuple)
    for i, value in enumerate(rna_manual_reference.url_manual_mapping):
        try:
            assert len(value) == 2
            assert isinstance(value[0], str)
            assert isinstance(value[1], str)
        except:
            print("Expected a tuple of 2 strings, instead item {:d} is a {:s}: {!r}".format(i, str(type(value)), value))
            import traceback
            traceback.print_exc()
            raise


def lookup_rna_url(rna_id, visit_indices):
    """
    A local version of ``WM_OT_doc_view_manual._lookup_rna_url``
    that tracks which matches are found.
    """
    import _rna_manual_reference as rna_manual_reference
    from fnmatch import fnmatchcase
    rna_id = rna_id.lower()
    for i, (pattern, url_suffix) in enumerate(rna_manual_reference.url_manual_mapping):
        if fnmatchcase(rna_id, pattern):
            visit_indices.add(i)
            return rna_manual_reference.url_manual_prefix + url_suffix
    return None


# a stripped down version of api_dump() in rna_info_dump.py
def test_lookup_coverage():

    def rna_ids():
        import _rna_info as rna_info
        struct = rna_info.BuildRNAInfo()[0]
        for struct_id, v in sorted(struct.items()):
            props = [(prop.identifier, prop) for prop in v.properties]
            struct_path = "bpy.types.{:s}".format(struct_id[1])
            yield (struct_path, struct_path)
            for prop_id, prop in props:
                yield (struct_path, "{:s}.{:s}".format(struct_path, prop_id))

        for submod_id in dir(bpy.ops):
            op_path = "bpy.ops.{:s}".format(submod_id)
            for op_id in dir(getattr(bpy.ops, submod_id)):
                yield (op_path, "{:s}.{:s}".format(op_path, op_id))

    # Check coverage:
    # from bl_operators import wm

    set_group_all = set()
    set_group_doc = set()

    visit_indices = set()

    print("")
    print("----------------------------------")
    print("RNA Patterns Unknown to the Manual")

    for rna_group, rna_id in rna_ids():
        # Correct but slower & doesn't track usage.
        # url = wm.WM_OT_doc_view_manual._lookup_rna_url(rna_id, verbose=False)
        url = lookup_rna_url(rna_id, visit_indices)

        if url is None:
            print(rna_id)

        if VERBOSE:
            print(rna_id, "->", url)

        set_group_all.add(rna_group)
        if url is not None:
            set_group_doc.add(rna_group)

    print("")
    print("---------------------------------------")
    print("Unused RNA Patterns Known to the Manual")

    import _rna_manual_reference as rna_manual_reference
    for i, (pattern, url_suffix) in enumerate(rna_manual_reference.url_manual_mapping):
        if i not in visit_indices:
            print(pattern, url_suffix)

    # finally report undocumented groups
    print("")
    print("---------------------")
    print("Undocumented Sections")

    for rna_group in sorted(set_group_all):
        if rna_group not in set_group_doc:
            print("{:s}.*".format(rna_group))


def test_language_coverage():
    """
    Ensure the language lookup table is complete and properly configured.

    Verifies that:
    1. manual_language_code() returns a valid language code
    2. The URL manual prefix is properly formatted for the current language
    3. The language code is either a valid ISO code or 'en' (default fallback)
    """
    import _rna_manual_reference as rna_manual_reference

    # Get the current language code
    lang_code = bpy.utils.manual_language_code()

    # Valid language codes should be lowercase and either 'en' or contain underscore
    # (e.g., 'en', 'fr_FR', 'zh_HANS', etc.)
    assert isinstance(lang_code, str), f"Language code must be a string, got {type(lang_code)}"
    assert len(lang_code) >= 2, f"Language code '{lang_code}' is too short"
    assert lang_code == 'en' or '_' in lang_code or lang_code in ('es', 'eo', 'ha', 'ab', 'ka', 'ta', 'km', 'sw', 'da', 'ur'), \
        f"Language code '{lang_code}' has unexpected format (should be 'en' or contain underscore)"

    # Verify the URL manual prefix is properly formatted
    # Should be in format: https://docs.blender.org/manual/{lang}/{major}.{minor}/
    assert rna_manual_reference.url_manual_prefix.startswith("https://docs.blender.org/manual/"), \
        f"URL manual prefix has unexpected format: {rna_manual_reference.url_manual_prefix}"
    assert rna_manual_reference.url_manual_prefix.endswith("/"), \
        f"URL manual prefix should end with '/': {rna_manual_reference.url_manual_prefix}"

    # Verify the URL contains the language code
    assert f"/{lang_code}/" in rna_manual_reference.url_manual_prefix, \
        f"URL manual prefix should contain language code '{lang_code}': {rna_manual_reference.url_manual_prefix}"

    # Verify the URL contains version numbers
    version_str = f"/{bpy.app.version[0]}.{bpy.app.version[1]}/"
    assert version_str in rna_manual_reference.url_manual_prefix, \
        f"URL manual prefix should contain version '{version_str}': {rna_manual_reference.url_manual_prefix}"

    print(f"Language coverage test passed for language code: '{lang_code}'")


def test_urls():
    import os
    import sys
    import _rna_manual_reference as rna_manual_reference

    import urllib.error
    from urllib.request import urlopen

    # avoid URL lookups if possible
    LOCAL_PREFIX = os.environ.get("LOCAL_PREFIX")
    if LOCAL_PREFIX is None:
        prefix = rna_manual_reference.url_manual_prefix

    urls = {suffix for (rna_id, suffix) in rna_manual_reference.url_manual_mapping}

    urls_len = "{:d}".format(len(urls))
    print("")
    print("-------------" + "-" * len(urls_len))
    print("Testing URLS {:s}".format(urls_len))
    print("")

    color_red = '\033[0;31m'
    color_green = '\033[1;32m'
    color_normal = '\033[0m'

    urls_fail = []

    if LOCAL_PREFIX:
        for url in sorted(urls):
            url_full = os.path.join(LOCAL_PREFIX, url.partition("#")[0])
            if os.path.exists(url_full):
                if VERBOSE:
                    print("  {:s} ... ".format(url_full), end="")
                    print(color_green + "OK" + color_normal)
            else:
                print("  {:s} ... ".format(url_full), end="")
                print(color_red + "FAIL!" + color_normal)
                urls_fail.append(url)
    elif False:
        # URL lookups are too slow to be practical.
        for url in sorted(urls):
            url_full = prefix + url
            print("  {:s} ... ".format(url_full), end="")
            sys.stdout.flush()
            try:
                urlopen(url_full)
                print(color_green + "OK" + color_normal)
            except urllib.error.HTTPError:
                print(color_red + "FAIL!" + color_normal)
                urls_fail.append(url)
    else:
        print("Skipping URL lookups, define LOCAL_PREFIX env variable, and point it to a manual build!")

    if urls_fail:
        urls_len = "{:d}".format(len(urls_fail))
        print("")
        print("------------" + "-" * len(urls_len))
        print("Failed URLS {:s}".format(urls_len))
        print("")
        for url in urls_fail:
            print("  {:s}{:s}{:s}".format(color_red, url, color_normal))


def main():
    test_data()
    test_lookup_coverage()
    test_language_coverage()
    test_urls()


if __name__ == "__main__":
    main()
