"""
Analyze the results of checking triples from results.txt
"""

from pathlib import Path
from re import findall
from more_itertools import chunked
from ast import literal_eval


def main() -> None:
    """
    Open the results file, grab the output of each crash, and
    sort based on the backtrace to minimize the test cases
    """
    results = Path("./results.txt").read_text(encoding="utf-8", errors="ignore")
    stack_traces = {}

    STACK_TRACE_RE = rb"\#[0-9]+\s+0x[0-9a-f]+\s+([a-zA-Z_0-9:~]+)"

    for result, output_string in chunked(results.splitlines(), 2):
        strace = (*findall(STACK_TRACE_RE, literal_eval(output_string)),)
        # if strace not in stack_traces:
        #     print(strace)
        stack_traces[strace] = (result, literal_eval(output_string))

    for stack_trace in stack_traces:
        print(stack_trace)
        print(stack_traces[stack_trace][0])


if __name__ == "__main__":
    main()
