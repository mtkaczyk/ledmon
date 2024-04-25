#!/usr/bin/python3.11

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 Intel Corporation.

import argparse, logging, os, re, sys
from typing import NamedTuple

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

comment_marks = {
    ".c": '//',
    ".h": '//',
    ".am": '#',
    ".sh": '#',
    ".ac": '#',
    ".py": '#',
    ".pod": '#',
}


#FIXME: Should it be configurable by Yaml?
class Directory_license(NamedTuple):
    licenses: dict[str, set[str]]


DIRECTORY_LICENSES: dict[str, Directory_license] = {
    "src/ledctl":
    Directory_license(licenses={
        ".c": ["GPL-2.0-only"],
        ".h": ["GPL-2.0-only"],
        ".am": ["GPL-2.0-only"],
    }),
    "src/ledmon":
    Directory_license(
        licenses={
            ".c": ["GPL-2.0-only", "LGPL-2.1-or-later"],
            ".h": ["GPL-2.0-only", "LGPL-2.1-or-later"],
            ".am": ["GPL-2.0-only", "GPL-3.0-or-later"],
        }),
    # NOTE: Files in lib directory must be released under LGPL, be careful when extending.
    "src/lib":
    Directory_license(
        licenses={
            ".c": ["LGPL-2.1-or-later"],
            ".h": ["LGPL-2.1-or-later"],
            ".am": ["GPL-2.0-only"],
        }),
    "config":
    Directory_license(licenses={
        ".h": ["LGPL-2.1-or-later"],
    }),
    # Default, used if file is not placed in directory explicitly listed
    ".":
    Directory_license(
        licenses={
            ".c": ["GPL-2.0-only", "GPL-3.0-or-later"],
            ".h": ["GPL-2.0-only"],
            ".am": ["GPL-2.0-only", "GPL-3.0-or-later"],
            ".sh": ["GPL-2.0-only", "GPL-3.0-or-later"],
            ".ac": ["GPL-3.0-or-later"],
            ".py": ["GPL-3.0-or-later"],
            ".pod": ["GPL-2.0-only"]
        }),
}


# It compares DIRECTORY_LICENSES keys, first match wins. Order matters
def get_allowed_licenses(path):
    cwd = os.getcwd()

    for key_dir in DIRECTORY_LICENSES.keys():
        subpath = os.path.realpath(f"{cwd}/{key_dir}")

        if os.path.dirname(path).startswith(subpath):
            return DIRECTORY_LICENSES[key_dir].licenses

    raise Exception(f"Error finding any allowed licenses for file {path}")


def check_license_header(path, first_line, file_type):
    allowed_licenses = get_allowed_licenses(path)
    comment_mark = comment_marks[file_type]

    for license in allowed_licenses[file_type]:
        license_string = f"{comment_mark} SPDX-License-Identifier: {license}"
        LOGGER.debug(F"Checking for \"{license_string}\" license string")

        if license_string == first_line:
            return True

    return False


# There are no strong requirements for copyrights and how ofter they should be updated.
# Keep them in simple form "Copyright (C) <date> Intel Corporation." to not have to update them
# before each release.
def check_Intel_copyright(line):
    copyright = line.partition('Copyright ')[2]
    regex_pat = r"\(C\) 20[0-9]{2} Intel Corporation.$"

    copyright_line_re = re.compile(regex_pat)

    match = copyright_line_re.match(copyright)
    if match is None:
        raise Exception(
            f"\'{copyright}\' is Intel Copyright in not expected format \'{regex_pat}\'"
        )


def check_copyright_line(line, file_type):
    comment_mark = comment_marks[file_type]

    if not line.startswith(f"{comment_mark} Copyright"):
        raise Exception(f'\"{line}\" is not Copyright line')

    if "Intel" in line:
        check_Intel_copyright(line)


def check_licensing(path):
    file_type = os.path.splitext(path)[1]
    file = open(path)
    line = file.readline().strip()

    if line.startswith("#!/"):
        # Here comes the interpreter. We expect, SPDX in third line but second line must be empty.
        assert file.readline().strip() == ""
        line = file.readline().strip()

    if check_license_header(path, line, file_type) == False:
        raise Exception(f"Checking for license in {path} - FAILED")

    # Loop for Copyrights. Scan them until empty line is reached.
    while True:
        line = file.readline().strip()
        if line == "":
            return
        check_copyright_line(line, file_type)


def main():

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    LOGGER.addHandler(ch)

    if not os.path.exists(f"{os.getcwd()}/tests/licensing.py"):
        LOGGER.error(
            "The test must be run main repo directory e.g. ./tests/licensing.py"
        )
        return 1

    parser = argparse.ArgumentParser(
        prog="licensing.py", description='Check licenses used in code.')

    parser.add_argument(
        '-f',
        '--file',
        action='append',
        required=True,
        help='file or dir path to scan, Can be specified multiple times.')
    parser.add_argument('-l',
                        '--log-level',
                        action='store',
                        required=False,
                        help="Log level, use python logging module log levels")

    args = parser.parse_args()

    if args.log_level:
        ch.setLevel(logging.getLevelNamesMapping()[args.log_level])

    path = os.getcwd()

    files = []

    # Normalize them to full paths
    for file in args.file:
        files.append(f"{path}/{file}")

    for file in files:
        check_licensing(file)

    LOGGER.info("TEST PASSED")


if __name__ == '__main__':
    sys.exit(main())
