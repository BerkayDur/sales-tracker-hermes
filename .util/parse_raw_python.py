'''Parse a raw Python file to json, specifically for use in a GitHub workflow for
updating creating a json to be parsed and used for creating a badge.'''

import json
import re
import argparse


def init_parser():
    '''Setups an argument parser that reads 2 parameters, input and output. These
    This is to be used by the GitHub workflow to obtain input/output file information.'''
    arg_parse = argparse.ArgumentParser(
        description="Get input/output files at runtime")
    arg_parse.add_argument('--input', '--i', type=str,
                           help="relative file path to input file.")
    arg_parse.add_argument('--output', '--o', type=str,
                           help="relative file path to output file.")
    arg_parse.add_argument('--type', '--t', type=str,
                           choices=["pytest", "pylint"],
                           help="The type of evaluation being performed.")
    return arg_parse


def read_file(file_name: str) -> str:
    '''Read a file and return its contents as a string'''
    with open(file_name, mode='r', encoding='utf-8') as f:
        content = f.read()
    return content


def get_total_number_of_failed_tests(content: str) -> int:
    '''Calculate the number of failed tests in contents. This works specifically
    for pytest tests.'''
    if 'no tests ran' in content:
        return 0
    try:
        return int(re.findall(r'\d+(?= failed)', content)[0])
    except IndexError:
        return 0


def get_total_number_of_passed_tests(content: str) -> int:
    '''Calculate the number of failed tests in contents. This works specifically
    for pytest tests.'''
    if 'no tests ran' in content:
        return 0
    try:
        return int(re.findall(r'\d+(?= passed)', content)[0])
    except IndexError:
        return 0


def get_avg_pylint_scores(content: str) -> list[float]:
    '''Get the average pylint scores across all the tests completed.'''
    matches = re.findall(
        r'(?<=Your code has been rated at )\d+\.?\d+(?=/10)', content)
    if len(matches) == 0:
        return [0.0]
    return [float(match) for match in matches]


def calculate_avg_percentage_of_passed_tests(passed_tests: int, total_tests: int) -> int:
    '''Calculate the mean percentage passed tests given passed tests and total tests.'''
    if passed_tests == 0:
        return 0
    return int(100 * passed_tests / total_tests)


def calculate_avg_pylint_score(pylint_scores: list[float]) -> float:
    '''Calculate the mean pylint score across all the pylint tests.'''
    return sum(pylint_scores) / len(pylint_scores)


def create_dict_of_pytest_scores(passed_tests: int,
                                 failed_tests: int,
                                 total_tests: int,
                                 percentage_of_passing_tests: int) -> dict:
    '''Create dictionary of pytest scores given the relevant information.'''
    return {
        'passed': passed_tests,
        'failed': failed_tests,
        'total': total_tests,
        'passed_percentage': percentage_of_passing_tests
    }


def create_dict_of_pylint_scores(avg_score: float) -> dict:
    '''Create dictionary of pylint scores given the average score.'''
    return {
        'avg_score': avg_score
    }


def create_json(scores: dict, write_file: str) -> None:
    '''Create a json and dump a dictionary to it.'''
    with open(write_file, encoding='utf-8', mode='w') as f:
        json.dump(scores, f)


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()
    file_content = read_file(args.input)
    if args.type == 'pytest':
        FAILED = get_total_number_of_failed_tests(file_content)
        PASSED = get_total_number_of_passed_tests(file_content)
        total = FAILED + PASSED
        PERCENTAGE_PASSED = calculate_avg_percentage_of_passed_tests(
            PASSED, total)
        score = create_dict_of_pytest_scores(
            PASSED, FAILED, total, PERCENTAGE_PASSED)
        create_json(score, args.output)
    elif args.type == 'pylint':
        AVG_PYLINT_SCORES = get_avg_pylint_scores(file_content)
        AVG_PYLINT_SCORE = calculate_avg_pylint_score(AVG_PYLINT_SCORES)
        score = create_dict_of_pylint_scores(AVG_PYLINT_SCORE)
        create_json(score, args.output)
