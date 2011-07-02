
import ConfigParser
from githubcollective.team import Team
from githubcollective.repo import Repo

BASE_URL = 'https://api.github.com'
TEAM_PREFIX = '--auto-'
TEAM_OWNERS_SUFFIX = '-owners'


class Config(object):

    _teams = {}
    _repos = {}
    _fork_urls = {}

    def __init__(self, filename):
        config = ConfigParser.SafeConfigParser()
        config.read(filename)

        for section in config.sections():
            if section.startswith('repo:'):
                # add repo
                name = section[len('repo:'):]
                self._repos[name] = Repo(name)
                # add fork
                self._fork_urls[name] = None
                if config.has_option(section, 'fork'):
                    self._fork_urls[name] = config.get(section, 'fork')
                # add owners team
                team_name = TEAM_PREFIX + name + TEAM_OWNERS_SUFFIX
                team_members = config.get(section, 'owners').split()
                self._teams[team_name] = Team(team_name, 'admin',
                        members=team_members, repos=[name])
            elif section.startswith('team:'):
                # add team
                name = TEAM_PREFIX + section[len('team:'):]
                permission = 'pull'
                if config.has_option(section, 'permission'):
                    permission = config.get(section, 'permission')
                members = []
                if config.has_option(section, 'members'):
                    members = config.get(section, 'members').split()
                repos = []
                if config.has_option(section, 'repos'):
                    repos = config.get(section, 'repos').split()
                self._teams[name] = Team(name, permission,
                        members=members, repos=repos)

        # add repos to teams (defined with repo: section
        for section in config.sections():
            if section.startswith('repo:'):
                repos = [section[len('repo:'):]]
                if config.has_option(section, 'teams'):
                    for team in config.get(section, 'teams').split():
                        self._teams[TEAM_PREFIX + team].repos.update(repos)


    @property
    def teams(self):
        return set(self._teams.keys())

    def get_team(self, name):
        return self._teams.get(name, None)

    def get_team_members(self, name):
        members = []
        team = self.get_team(name)
        if team:
            members = team.members
        return set(members)

    def get_team_repos(self, name):
        repos = []
        team = self.get_team(name)
        if team:
            repos = team.repos
        return set(repos)

    @property
    def repos(self):
        return set(self._repos.keys())

    def get_repo(self, name):
        return self._repos.get(name, None)

    def get_fork_url(self, repo):
        return self._fork_urls.get(repo, None)
