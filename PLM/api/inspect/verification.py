# -*- coding: utf-8 -*-
"""

Script Name: 
Author: Do Trinh/Jimmy - 3D artist.

Description:


"""
# -------------------------------------------------------------------------------------------------------------
import logging

from plumbum import CommandNotFound, local

log = logging.getLogger(__name__)

def dry_run(command, dry_run):
    """Executes a shell command unless the dry run option is set"""
    if not dry_run:
        cmd_parts = command.split(' ')
        # http://plumbum.readthedocs.org/en/latest/local_commands.html#run-and-popen
        return local[cmd_parts[0]](cmd_parts[1:])
    else:
        log.info('Dry run of %s, skipping' % command)
    return True


def get_test_runner():
    test_runners = ['tox', 'nosetests', 'py.test']
    test_runner = None
    for runner in test_runners:
        try:
            test_runner = local[runner]
        except CommandNotFound:
            continue
    return test_runner


def run_tests():
    """Executes your tests."""
    test_runner = get_test_runner()
    if test_runner:
        result = test_runner()
        log.info('Test execution returned:\n%s' % result)
        return result
    else:
        log.info('No test runner found')

    return None


def run_test_command(context):
    if context.test_command:
        result = dry_run(context.test_command, context.dry_run)
        log.info('Test command "%s", returned %s', context.test_command, result)
    return True

# -------------------------------------------------------------------------------------------------------------
# Created by Trinh Do on 5/6/2020 - 3:13 AM
# © 2017 - 2020 DAMGteam. All rights reserved
