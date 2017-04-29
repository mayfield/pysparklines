# vim: set fileencoding=utf-8 :
from __future__ import print_function

import itertools
import math
import os
import re
import sys

# Eight unicode characters of (nearly) steadily increasing height.
spark_chars = u"▁▂▃▄▅▆▇█"

braile_ref = '''
    ⡀⡁⡂⡃⡄⡅⡆⡇⡈⡉⡊⡋⡌⡍⡎⡏
    ⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟
    ⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯
    ⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿
    ⢀⢁⢂⢃⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏
    ⢐⢑⢒⢓⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟
    ⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯
    ⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿
    ⣀⣁⣂⣃⣄⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏
    ⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞⣟
    ⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯
    ⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿
'''

compressed_dots = (
    ' ⢀⢠⢰⢸',
    '⡀⣀⣠⣰⣸',
    '⡄⣄⣤⣴⣼',
    '⡆⣆⣦⣶⣾',
    '⡇⣇⣧⣷⣿',
)


def _convert_to_float(i):
    try:
        return float(i)
    except:
        return None


def dotify(series):
    """ Use dot based graphing (denser). """
    # quantify data into 0->4 ints.
    low = min(series)
    normalized = [x - low for x in series]
    high = max(normalized) or 1
    quantum = len(compressed_dots[0]) - 1
    quantized = [round((x / high) * quantum) for x in normalized]
    if len(quantized) % 2 == 1:
        qiter = itertools.chain(quantized, [0])
    else:
        qiter = iter(quantized)
    buf = []
    for x1 in qiter:
        x2 = next(qiter)
        buf.append(compressed_dots[x1][x2])
    return ''.join(buf)


def sparkify(series, minimum=None, maximum=None):
    u"""Converts <series> to a sparkline string.

    Example:
    >>> sparkify([ 0.5, 1.2, 3.5, 7.3, 8.0, 12.5, 13.2, 15.0, 14.2, 11.8, 6.1,
    ... 1.9 ])
    u'▁▁▂▄▅▇▇██▆▄▂'

    >>> sparkify([1, 1, -2, 3, -5, 8, -13])
    u'▆▆▅▆▄█▁'

    Raises ValueError if input data cannot be converted to float.
    Raises TypeError if series is not an iterable.
    """
    series = [ float(i) for i in series ]
    if minimum is None:
        minimum = min(series)
    if maximum is None:
        maximum = max(series)
    data_range = maximum - minimum
    if data_range == 0.0:
        # Graph a baseline if every input value is equal.
        return u''.join([ spark_chars[0] for i in series ])
    coefficient = (len(spark_chars) - 1.0) / data_range
    return u''.join([
        spark_chars[
            int(round((x - minimum) * coefficient))
        ] for x in series
    ])

def guess_series(input_string):
    u"""Tries to convert <input_string> into a list of floats.

    Example:
    >>> guess_series("0.5 1.2 3.5 7.3 8 12.5, 13.2,"
    ... "15.0, 14.2, 11.8, 6.1, 1.9")
    [0.5, 1.2, 3.5, 7.3, 8.0, 12.5, 13.2, 15.0, 14.2, 11.8, 6.1, 1.9]
    """
    float_finder = re.compile("([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)")
    return ([
        i for i in [
            _convert_to_float(j) for j in float_finder.findall(input_string)
        # Remove entires we couldn't convert to a sensible value.
        ] if i is not None and not math.isnan(i) and not math.isinf(i)
    ])


def main():
    u"""Reads from command line args or stdin and prints a sparkline from the
    data.  Requires at least 2 data points as input.
    """
    import argparse
    from pkg_resources import require

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "data",
        nargs=argparse.REMAINDER,
        help="Floating point data, any delimiter."
    )
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Display the version number and exit."
    )
    args = parser.parse_args()

    if args.version:
        version = require("pysparklines")[0].version
        print(version)
        sys.exit(0)

    if os.isatty(0) and not args.data:
        parser.print_help()
        sys.exit(1)
    elif args.data:
        arg_string = u' '.join(args.data)
    else:
        arg_string = sys.stdin.read()

    try:
        output = sparkify(guess_series(arg_string))
    except:
        sys.stderr.write("Could not convert input data to valid sparkline\n")
        sys.exit(1)

    print(output.encode('utf-8', 'ignore'))

if __name__ == "__main__":
    main()
