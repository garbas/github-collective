
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

    def __init__(self, filename, verbose, pretend):
        self._teams = {}
        self._repos = {}
        self._fork_urls = {}

        self.filename = filename
        self.verbose = verbose
        self.pretend = pretend

        if type(filename) is file:
            data = filename.read()
        elif type(filename) in [str, unicode] and \
             self.is_url(filename):
            response = requests.get(filename)
            response.raise_for_status()
            data = response.text
        elif type(filename) in [str, unicode] and \
             os.path.exists(filename):
            f = open(filename)
            data = f.read()
            f.close()
        else:
            data = filename

        if data:
            self._teams, self._repos, self._fork_urls = self.parse(data)

    def parse(self, data):
        teams, repos = {}, {}
        data = json.loads(data)

        for team in data['teams']:
            team = Team(**team)
            teams[team.name] = team

        for repo in data['repos']:
            repo = Repo(**repo)
            repos[repo.name] = repo

        return teams, repos, data['fork_urls']

    def dumps(self, cache):
        if cache.mode != 'w+':
            cache = open(cache.name, 'w+')
        cache.truncate(0)
        cache.seek(0)
        json.dump({
            'teams': [self._teams[name].dumps() for name in self.teams],
            'repos': [self._repos[name].dumps() for name in self.repos],
            'fork_urls': self._fork_urls,
            }, cache, indent=4)

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
        teams, repos, fork_urls = {}, {}, {}
        config = ConfigParser.SafeConfigParser()
        config.readfp(StringIO.StringIO(data))

        for section in config.sections():
            if section.startswith('repo:'):
                # add repo
                name = section[len('repo:'):]
                repos[name] = Repo(name)
                # add fork
                if config.has_option(section, 'fork'):
                    fork_urls[name] = config.get(section, 'fork')
                # add owners team
                if config.has_option(section, 'owners'):
                    team_name = TEAM_PREFIX + name + TEAM_OWNERS_SUFFIX
                    team_members = config.get(section, 'owners').split()
                    teams[team_name] = Team(team_name, 'admin',
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
                team_repos = []
                if config.has_option(section, 'repos'):
                    team_repos = config.get(section, 'repos').split()
                teams[name] = Team(name, permission,
                        members=members, repos=team_repos)

        # add repos to teams (defined with repo: section
        for section in config.sections():
            if section.startswith('repo:'):
                if config.has_option(section, 'teams'):
                    for team in config.get(section, 'teams').split():
                        teams[TEAM_PREFIX + team].repos.add(
                                section[len('repo:'):],
                                )

        return teams, repos, fork_urls

class ConfigGithub(Config):

    def __init__(self, github, cache, verbose=False, pretend=False):
        self.github = github
        self._github = {'teams': {}, 'repos': {}}

        data = None
        if cache:
            data = cache.read()
        super(ConfigGithub, self).__init__(data, verbose, pretend)
        if cache and not data:
            print 'CACHE DOES NOT EXISTS! CACHING...'
            self.dumps(cache)
            print 'CACHE WRITTEN TO %s!' % cache.name

    def _get_teams(self):
        if 'teams' not in self._github.keys() or \
           not self._github['teams']:
            self._github['teams'] = {}
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
                self._github['teams'][team.name] = team
        return self._github['teams']
    def _set_teams(self, value):
        self._github['teams'] = value
    def _del_teams(self):
        del self._github['teams']
    _teams = property(_get_teams, _set_teams, _del_teams)

    def _get_repos(self):
        if 'repos' not in self._github.keys() or \
           not self._github['repos']:
            self._github['repos'] = {}
            for item in self.github._gh_org_repos():
                repo = Repo(**item)
                self._github['repos'][repo.name] = repo
        return self._github['repos']
    def _set_repos(self, value):
        self._github['repos'] = value
    def _del_repos(self):
        del self._github['repos']
    _repos = property(_get_repos, _set_repos, _del_repos)

