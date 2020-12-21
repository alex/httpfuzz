import sre_parse
import re

import pytest


def extract_literals(r):
    ops = sre_parse.parse(r.pattern)
    results = []
    extract_literals_from_ops(ops, results)
    return results


def extract_literals_from_ops(ops, results):
    i = 0
    while i < len(ops):
        op, val = ops[i]
        if op == sre_parse.LITERAL:
            start_i = i
            while i < len(ops) and ops[i][0] == sre_parse.LITERAL:
                i += 1
            results.append("".join(chr(c) for _, c in ops[start_i:i]))
            continue
        elif op == sre_parse.BRANCH:
            _, branches = val
            for branch in branches:
                extract_literals_from_ops(branch, results)
        elif op == sre_parse.SUBPATTERN:
            _, _, _, sub_ops = val
            extract_literals_from_ops(sub_ops, results)
        elif op == sre_parse.MAX_REPEAT:
            _, _, sub_ops = val
            extract_literals_from_ops(sub_ops, results)
        elif op == sre_parse.ASSERT or op == sre_parse.ASSERT_NOT:
            _, sub_ops = val
            extract_literals_from_ops(sub_ops, results)
        i += 1
    return results


@pytest.mark.parametrize(
    ("r", "expected"),
    [
        (r"^abc$", ["abc"]),
        (r"abc|def", ["abc", "def"]),
        (r"(abc|\d+)", ["abc"]),
        (r"(?:abc){3,}", ["abc"]),
        (r"(?:abc){,3}", ["abc"]),
        (r"(?=abc)", ["abc"]),
        (r"(?!abc)", ["abc"]),
        (r"(?<=abc)", ["abc"]),
        (r"(?<!abc)", ["abc"]),
    ]
)
def test_extract_literals(r, expected):
    actual = extract_literals(re.compile(r))
    assert actual == expected