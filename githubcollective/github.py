
try:
    import simplejson as json
except:
    import json

import base64
import requests

from githubcollective.team import Team
from githubcollective.repo import Repo
from githubcollective.config import BASE_URL
from githubcollective.config import TEAM_PREFIX


class Github(object):
    """
    """

    _cache = {}

    _request_count = 0
    _request_limit = 5000
    _request_remaining = 5000

    def __init__(self, organization, username, password, verbose, pretend):
        self.org = organization
        self.verbose = verbose
        self.pretend = pretend
        self.headers = {
            'Authorization': 'Basic %s' % base64.encodestring(
                '%s:%s' % (username, password)).replace('\n', '')
            }

    #
    # requests library helpers

    def _request(self, method, url, data=None):
        kw = {'url': BASE_URL+url+'?per_page=10000',
              'headers': self.headers}
        if data:
            kw['data'] = data
        response = method(**kw)
        self._request_count += 1
        self._request_limit = response.headers['x-ratelimit-limit']
        self._request_remaining = response.headers['x-ratelimit-remaining']
        response.raise_for_status()
        if self.verbose:
            print '%s - %s/%s - %s - %s' % (
                self._request_count,
                self._request_remaining,
                self._request_limit,
                method.__name__.upper(),
                kw['url'],
                )
        return response

    def _get_request(self, url):
        return json.load(self._request(requests.get, url))

    def _delete_request(self, url):
        return self._request(requests.delete, url)

    def _post_request(self, url, data):
        return json.load(self._request(requests.post, url, data))

    def _put_request(self, url):
        return self._request(requests.put, url)

    def _patch_request(self, url, data):
        return self._request(requests.patch, url, data)

    #
    # github api helpers

    def _gh_org_teams(self):
        return self._get_request('/orgs/%s/teams' % self.org)

    def _gh_team(self, team_id):
        return self._get_request('/teams/%s' % team_id)

    def _gh_team_members(self, team_id):
        return self._get_request('/teams/%s/members' % team_id)

    def _gh_team_repos(self, team_id):
        return self._get_request('/teams/%s/repos' % team_id)

    def _gh_org_repos(self):
        return self._get_request('/orgs/%s/repos' % self.org)

    def _gh_org_fork_repo(self, fork_url):
        return self._post_request('/repos/%s/forks' % fork_url, {'org': self.org})

    def _gh_org_create_repo(self, name):
        return self._post_request('/orgs/%s/repos' % self.org, {'name': name})

    def _gh_org_create_team(self, name, permission='pull'):
        assert permission in ['pull', 'push', 'admin']
        return self._post_request('/orgs/%s/teams' % self.org, json.dumps({
            'name': name,
            'permission': permission,
            }))

    def _gh_org_edit_team(self, id, name, permission=None):
        data = {'name': name}
        if permission is not None:
            data['permission'] = permission
        assert permission in ['pull', 'push', 'admin']
        return self._patch_request('/teams/%s' % id, json.dumps(data))

    def _gh_org_delete_team(self, id):
        return self._delete_request('/teams/%s' % id)

    def _gh_org_add_team_member(self, id, member):
        return self._put_request('/teams/%s/members/%s' % (id, member))

    def _gh_org_remove_team_member(self, id, member):
        return self._delete_request('/teams/%s/members/%s' % (id, member))

    def _gh_org_add_team_repo(self, id, repo):
        return self._put_request('/teams/%s/repos/%s/%s' % (id, self.org, repo))

    def _gh_org_remove_team_repo(self, id, repo):
        return self._delete_request('/teams/%s/repos/%s/%s' % (id, self.org, repo))

    #
    #

    @property
    def _teams(self):
        if 'teams' not in self._cache.keys():
            self._cache['teams'] = {}
            for item in self._gh_org_teams():
                if not item['name'].startswith(TEAM_PREFIX):
                    continue
                item.update(self._gh_team(item['id']))
                team = Team(**item)
                if team.members_count > 0:
                    team.members.update([i['login']
                            for i in self._gh_team_members(item['id'])])
                if team.repos_count > 0:
                    team.repos.update([i['name']
                            for i in self._gh_team_repos(item['id'])])
                self._cache['teams'][team.name] = team
        return self._cache['teams']

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
    def _repos(self):
        if 'repos' not in self._cache.keys():
            self._cache['repos'] = {}
            for item in self._gh_org_repos():
                repo = Repo(**item)
                self._cache['repos'][repo.name] = repo
        return self._cache['repos']

    @property
    def repos(self):
        return set(self._repos.keys())

    def get_repo(self, name):
        return self._repos[name]

    #
    # github specific

    def add_repo(self, repo):
        self._repos[repo.name] = repo
        if self.pretend:
            return
        return self._gh_org_create_repo(repo.name)

    def remove_repo(self, repo):
        del self._repos[repo.name]
        if self.pretend:
            return
        print 'SENDING EMAIL TO OWNER OF %s!' % repo
        return

    def fork_repo(self, fork_url, repo):
        self._repos[repo.name] = repo
        if self.pretend:
            return
        return self._gh_org_fork_repo(fork_url)

    def add_team(self, team):
        self._teams[team.name] = Team(team.name, team.permission)
        if self.pretend:
            return
        return self._gh_org_create_team(
                name=team.name,
                permission=team.permission,
                )

    def edit_team(self, team):
        if self.pretend:
            return
        return self._gh_org_edit_team(
                id=team.id,
                name=team.name,
                permission=team.permission,
                )

    def remove_team(self, team):
        del self._teams[team.name]
        if self.pretend:
            return
        return self._gh_org_delete_team(team.id)

    def add_team_member(self, team, member):
        team = self.get_team(team.name)
        team.members.update([member])
        if self.pretend:
            return
        return self._gh_org_add_team_member(team.id, member)

    def remove_team_member(self, team, member):
        team = self.get_team(team.name)
        team.members.remove(member)
        if self.pretend:
            return
        return self._gh_org_remove_team_member(team.id, member)

    def add_team_repo(self, team, repo):
        team = self.get_team(team.name)
        team.repos.update([repo])
        if self.pretend:
            return
        return self._gh_org_add_team_repo(team.id, repo)

    def remove_team_repo(self, team, repo):
        team = self.get_team(team.name)
        team.repos.remove(repo)
        if self.pretend:
            return
        return self._gh_org_remove_team_repo(team.id, repo)
