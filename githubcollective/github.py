
try:
    import simplejson as json
except:
    import json

import base64
import requests

from githubcollective.config import BASE_URL


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
        kw = {'url': BASE_URL + url + '?per_page=10000',
              'headers': self.headers}
        if data:
            kw['data'] = data
        response = method(**kw)
        self._request_count += 1
        self._request_limit = response.headers['x-ratelimit-limit']
        self._request_remaining = response.headers['x-ratelimit-remaining']
        if self.verbose:
            print '%s - %s/%s - %s - %s' % (
                self._request_count,
                self._request_remaining,
                self._request_limit,
                method.__name__.upper(),
                kw['url'],
                )
        response.raise_for_status()
        return response

    def _get_request(self, url):
        return json.loads(self._request(requests.get, url).text)

    def _delete_request(self, url):
        if self.pretend:
            return
        return self._request(requests.delete, url)

    def _post_request(self, url, data):
        if self.pretend:
            return
        return self._request(requests.post, url, data)

    def _put_request(self, url):
        if self.pretend:
            return
        return self._request(requests.put, url)

    def _patch_request(self, url, data):
        if self.pretend:
            return
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
        return self._post_request('/repos/%s/forks' % fork_url,
                {'org': self.org})

    def _gh_org_create_repo(self, name):
        return self._post_request('/orgs/%s/repos' % self.org, json.dumps({
            'name': name,
            }))

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
        return self._put_request('/teams/%s/repos/%s/%s' %
                (id, self.org, repo))

    def _gh_org_remove_team_repo(self, id, repo):
        return self._delete_request('/teams/%s/repos/%s/%s' %
                (id, self.org, repo))
