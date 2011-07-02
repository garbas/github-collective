
try:
    import simplejson as json
except:
    import json

import os
import requests
import ConfigParser
import StringIO
from githubcollective.team import Team
from githubcollective.repo import Repo


BASE_URL = 'https://api.github.com'
TEAM_PREFIX = '--auto-'
TEAM_OWNERS_SUFFIX = '-owners'


class Config(object):

    def __init__(self, filename):
        self._teams = {}
        self._repos = {}
        self._fork_urls = {}
        self.filename = filename
        if type(filename) is file:
            data = filename.read()
        elif type(filename) in [str, unicode] and \
             self.is_url(filename):
            response = requests.get(filename)
            response.raise_for_status()
            data = response.read()
        elif type(filename) in [str, unicode] and \
             os.path.exists(filename):
            f = open(filename)
            data = f.read()
            f.close()
        else:
            raise NotImplemented

        if data:
            self.parse(data)

    def parse(self, data):
        data = json.loads(data)
        for team in data['teams']:
            team = Team(**team)
            self._teams[team.name] = team
        for repo in data['repos']:
            repo = Repo(**repo)
            self._repos[repo.name] = repo

    def dumps(self, filename=None):
        if filename is None:
            filename = self.filename

        if type(filename) is file:
            f = filename
        elif self.is_url(filename):
            raise Exception('Can save only locally, not remotly. '
                'Wrong filename: %s!' % filename)
        else:
            f = open(filename, 'w+')

        json.dump({
            'teams': [self._teams[name].dumps() for name in self.teams],
            'repos': [self._repos[name].dumps() for name in self.repos],
            }, f)
        f.close()

    def is_url(self, url):
        return url.startswith('http')

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


class ConfigCFG(Config):

    def parse(self, data):
        config = ConfigParser.SafeConfigParser()
        config.readfp(StringIO.StringIO(data))

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
                    if config.has_option(section, 'team'):
                        for team in config.get(section, 'team').split():
                            self._teams[TEAM_PREFIX + team].repos.update(repos)

class ConfigGithub(Config):

    def __init__(self, github=None):
        self._cache = {}
        self.github = github

    @property
    def _teams(self):
        if 'teams' not in self._cache.keys():
            self._cache['teams'] = {}
            for item in self.github._gh_org_teams():
                if not item['name'].startswith(TEAM_PREFIX):
                    continue
                item.update(self.github._gh_team(item['id']))
                team = Team(**item)
                if team.members_count > 0:
                    team.members.update([i['login']
                            for i in self.github._gh_team_members(item['id'])])
                if team.repos_count > 0:
                    team.repos.update([i['name']
                            for i in self.github._gh_team_repos(item['id'])])
                self._cache['teams'][team.name] = team
        return self._cache['teams']

    @property
    def _repos(self):
        if 'repos' not in self._cache.keys():
            self._cache['repos'] = {}
            for item in self.github._gh_org_repos():
                repo = Repo(**item)
                self._cache['repos'][repo.name] = repo
        return self._cache['repos']

