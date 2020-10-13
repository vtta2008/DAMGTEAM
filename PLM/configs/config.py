# -*- coding: utf-8 -*-
"""

Script Name: 
Author: Do Trinh/Jimmy - 3D artist.

Description:


"""
# -------------------------------------------------------------------------------------------------------------
""" Import """

from pathlib import Path
import io, os
import attr, click, inflection, toml
from PLM.api.version import BumpVersion
from PLM.api.commands import debug, info, note
from PLM import CFG_DIR, __envKey__
from PLM.api import prompt

AUTH_TOKEN_ENVVAR = 'GITHUB_AUTH_TOKEN'
DEFAULT_CONFIG_FILE = os.path.join(CFG_DIR, 'default.cfg')
PROJECT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_FILE, '.{0}.toml'.format(__envKey__))
DEFAULT_RELEASES_DIRECTORY = 'docs/releases'




def configure_labels(github_labels):

    labels_keyed_by_name = {}
    for label in github_labels:
        labels_keyed_by_name[label['name']] = label

    # TODO: streamlined support for github defaults: enhancement, bug
    changelog_worthy_labels = prompt.choose_labels(
        [properties['name'] for _, properties in labels_keyed_by_name.items()])

    # TODO: apply description transform in labels_prompt function
    described_labels = {}

    # auto-generate label descriptions
    for label_name in changelog_worthy_labels:
        label_properties = labels_keyed_by_name[label_name]

        # Auto-generate description as pluralised titlecase label name
        label_properties['description'] = inflection.pluralize(inflection.titleize(label_name))
        described_labels[label_name] = label_properties

    return described_labels



@attr.s
class Changes(object):

    auth_token = attr.ib()

    @classmethod
    def load(cls):
        tool_config_path = Path(DEFAULT_CONFIG_FILE)

        tool_settings = None
        if tool_config_path.exists():
            tool_settings = Project(**(toml.load(tool_config_path.open())['changes']))

        # envvar takes precedence over config file settings
        auth_token = os.environ.get(AUTH_TOKEN_ENVVAR)

        if auth_token:
            info('Found Github Auth Token in the environment')
            tool_settings = Changes(auth_token=auth_token)
        elif not (tool_settings and tool_settings.auth_token):
            while not auth_token:
                info('No auth token found, asking for it')
                # to interact with the Git*H*ub API
                note('You need a Github Auth Token for changes to create a release.')
                click.pause(
                    'Press [enter] to launch the GitHub "New personal access '
                    'token" page, to create a token for changes.'
                )
                click.launch('https://github.com/settings/tokens/new')
                auth_token = click.prompt('Enter your changes token')

            if not tool_settings:
                tool_settings = Changes(auth_token=auth_token)

            tool_config_path.write_text(
                toml.dumps({'changes': attr.asdict(tool_settings)})
            )

        return tool_settings


@attr.s
class Project(object):

    releases_directory = attr.ib()
    repository = attr.ib(default=None)
    bumpversion = attr.ib(default=None)
    labels = attr.ib(default=attr.Factory(dict))

    @classmethod
    def load(cls, repository):
        changes_project_config_path = Path(PROJECT_CONFIG_FILE)
        project_settings = None

        if changes_project_config_path.exists():
            # releases_directory, labels
            project_settings = Project(
                **(toml.load(changes_project_config_path.open())['changes'])
            )

        if not project_settings:
            releases_directory = Path(
                click.prompt(
                    'Enter the directory to store your releases notes',
                    DEFAULT_RELEASES_DIRECTORY,
                    type=click.Path(exists=True, dir_okay=True),
                )
            )

            if not releases_directory.exists():
                debug(
                    'Releases directory {} not found, creating it.'.format(
                        releases_directory
                    )
                )
                releases_directory.mkdir(parents=True)

            project_settings = Project(
                releases_directory=str(releases_directory),
                labels=configure_labels(repository.labels),
            )
            # write config file
            changes_project_config_path.write_text(
                toml.dumps({'changes': attr.asdict(project_settings)})
            )

        project_settings.repository = repository
        project_settings.bumpversion = BumpVersion.load(repository.latest_version)

        return project_settings



# TODO: borg legacy
DEFAULTS = {'changelog': 'CHANGELOG.md', 'readme': 'README.md', 'github_auth_token': None, }


class Config:
    """Deprecated"""

    test_command = None
    pypi = None
    skip_changelog = None
    changelog_content = None
    repo = None

    def __init__(self, module_name, dry_run, debug, no_input, requirements, new_version,
                 current_version, repo_url, version_prefix,):

        self.module_name = module_name
        # module_name => project_name => curdir
        self.dry_run = dry_run
        self.debug = debug
        self.no_input = no_input
        self.requirements = requirements
        self.new_version = (version_prefix + new_version if version_prefix else new_version)
        self.current_version = current_version


def project_config():
    """Deprecated"""

    project_name = __envKey__

    config_path = os.path.join(project_name, PROJECT_CONFIG_FILE)

    if not os.path.exists(config_path):
        store_settings(DEFAULTS.copy())
        return DEFAULTS

    return toml.load(io.open(config_path)) or {}


def store_settings(settings):
    pass




# -------------------------------------------------------------------------------------------------------------
# Created by Trinh Do on 5/6/2020 - 3:13 AM
# © 2017 - 2020 DAMGteam. All rights reserved
