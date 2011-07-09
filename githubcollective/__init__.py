
import os
import sys
import argparse
from githubcollective.sync import Sync
from githubcollective.github import Github
from githubcollective.config import Config
from githubcollective.config import ConfigCFG
from githubcollective.config import ConfigGithub


def config_type(config):
    if config.endswith('.cfg'):
        return ConfigCFG, config
    elif config.endswith('.json'):
        return Config, config
    else:
        raise NotImplemented

def cache_type(cache):
    if os.path.exists(cache):
        f = open(cache)
        data = f.read()
        if data:
            f.seek(0)
            return f
        f.close()
    return open(cache, 'w+')

def run():
    parser = argparse.ArgumentParser(
        prog='github-collective',
        description='This tool will let you automate tedious tasks of '
                    'creating teams granting permission and creating '
                    'repositories.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

    parser.add_argument('-c', '--config', type=config_type, required=True,
            help="path to configuration file (could also be remote location). "
                 "eg. http://collective.github.com/permissions.cfg")
    parser.add_argument('-C', '--cache', type=cache_type,
            help="path to file where to cache results from github.",
            default=None)
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

    new = args.config[0](
            args.config[1],
            args.verbose,
            args.pretend,
            )

    old = ConfigGithub(
            github,
            args.cache,
            args.verbose,
            args.pretend,
            )

    sync_ok = Sync(
            github,
            args.verbose,
            args.pretend,
            ).run(new, old)

    if sync_ok:
        if args.cache:
            if not args.pretend:
                old.dumps(args.cache)
            args.cache.close()
        sys.exit()
    sys.exit(1)
