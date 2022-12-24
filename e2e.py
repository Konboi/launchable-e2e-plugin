import click
from xml.etree import ElementTree as ET
from typing import Generator
from ..commands.record.case_event import CaseEvent, CaseEventType

from launchable.test_runners import launchable

@launchable.subset
def subset(client):
    # read lines as test file names
    for t in client.stdin():
        client.test_path(t.rstrip("\n"))
    client.separator = ","
    client.run()


@click.argument('reports', required=True, nargs=-1)
@launchable.record.tests
def record_tests(client, reports):
    for r in reports:
        client.report(r)

    def parse_func(p: str) -> Generator[CaseEventType, None, None]:
        tree = ET.parse(p)
        for use_case in tree.iter("UseCase"):

            if len(use_case) == 0:
                continue

            use_case_name = use_case.attrib.get('name')
            if use_case_name is None:
                continue

            for scenario in use_case.iter("Scenario"):
                if len(scenario) == 0:
                    continue

                scenario_name = scenario.attrib.get('name')
                for testcase in scenario.iter('TestCase'):
                    testcase_name = testcase.attrib.get('name')
                    duration = testcase.attrib.get('time')
                    result = testcase.attrib.get('result')

                    status = 0
                    if result == 'error':
                        status = 1

                    test_path = [
                        {"type": "UseCase", "name": use_case_name},
                        {"type": "Scenario", "name": scenario_name},
                        {"type": "TestCase", "name": testcase_name},
                    ]

                    yield CaseEvent.create(
                        test_path, duration, status, None, None, None, None)

    client.parse_func = parse_func
    client.run()


split_subset = launchable.CommonSplitSubsetImpls(__name__).split_subset()