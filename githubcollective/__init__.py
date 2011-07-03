
import os
import sys
import argparse
from githubcollective.sync import Sync
from githubcollective.github import Github
from githubcollective.config import Config
from githubcollective.config import ConfigCFG
from githubcollective.config import ConfigGithub


def select_config(config):
    if config.endswith('.cfg'):
        return ConfigCFG(config)
    elif config.endswith('.json'):
        return Config(config)
    else:
        raise NotImplemented


class Mailer(object):

    def __init__(self, type_):
        raise NotImplemented

    def send(self, to, msg):
        raise NotImplemented


def run():
    parser = argparse.ArgumentParser(
        prog='github-collective',
        description='This tool will let you automate tedious tasks of '
                    'creating teams granting permission and creating '
                    'repositories.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

    parser.add_argument('-c', '--config', type=select_config, required=True,
            help="path to configuration file (could also be remote location). "
                 "eg. http://collective.github.com/permissions.cfg")
    parser.add_argument('-M', '--mailer', type=lambda x: Mailer(x),
            help="TODO")
    parser.add_argument('-C', '--cache', type=str,
            help="path to file where to cache results from github.")
    parser.add_argument('-o', '--github-org', type=str, required=True,
            help="github organisation.")
    parser.add_argument('-u', '--github-username', type=str, required=True,
            help="github account username.")
    parser.add_argument('-P', '--github-password', type=str, required=True,
            help="github account password.")
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-p', '--pretend', action='store_true')

    args = parser.parse_args()

    github = Github(
                args.github_org,
                args.github_username,
                args.github_password,
                args.verbose,
                args.pretend,
                )

    new = args.config
    old = None
    if args.cache and \
       os.path.exists(args.cache):
        old = Config(args.cache)
    if old is None or \
       (not old.teams and not old.repos):
        old = ConfigGithub(github)

    sync = Sync(github,
            mailer=args.mailer,
            verbose=args.verbose,
            pretend=args.pretend,
            )
    sync_ok = sync.run(new, old)

    if sync_ok:
        if args.cache and \
           (not args.pretend or not os.path.exists(args.cache)):
            cache = open(args.cache, 'w+')
            old.dumps(cache)
            cache.close()
        sys.exit()
    sys.exit(1)
