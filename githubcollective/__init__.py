
import sys
import argparse
from githubcollective.config import Config
from githubcollective.github import Github
from githubcollective.sync import Sync


def run():
    """
    """

    parser = argparse.ArgumentParser(
        prog=Sync.__name__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    #parser.add_argument('-S', '--last-state',
    #        dest='state', type=argparse_file_type, required=True)
    #parser.add_argument('-L', '--log-directory',
    #        dest='log', type=argparse_log_type, required=True)

    parser.add_argument('-c', '--config',
            type=lambda x: Config(x), required=True)
    parser.add_argument('-o', '--github-organization',
            type=str, required=True)
    parser.add_argument('-u', '--github-username',
            type=str, required=True)
    parser.add_argument('-P', '--github-password',
            type=str, required=True)
    parser.add_argument('-v', '--verbose',
            action='store_true')
    parser.add_argument('-p', '--pretend',
            action='store_true')

    args = parser.parse_args()

    sync = Sync(verbose=args.verbose)
    sync_ok = sync.run(
            args.config,
            Github(
                args.github_organization,
                args.github_username,
                args.github_password,
                args.pretend,
                ),
            )

    if sync_ok:
        sys.exit()

    sys.exit(1)  # terminate with exit code 1
                 # meaning that sync had some problems
