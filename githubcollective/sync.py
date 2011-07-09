
try:
    import simplejson as json
except:
    import json

from githubcollective.team import Team


class Sync(object):

    def __init__(self, github, verbose=False, pretend=False):
        self.github = github
        self.verbose = verbose
        self.pretend = pretend

    def run(self, new, old):

        # CREATE (OR FORK) REPOS
        if self.verbose:
            print 'CREATED REPOS:'
        to_add = new.repos - old.repos
        for repo in to_add:
            fork_url = new.get_fork_url(repo)
            if fork_url is None:
                self.add_repo(old, new.get_repo(repo))
                if self.verbose:
                    print '    - %s' % repo
            else:
                self.fork_repo(old, fork_url, new.get_repo(repo))
                if self.verbose:
                    print '    - %s - FORK OF %s' % (repo, fork_url)

        # REMOVE REPOS
        if self.verbose:
            print 'REPOS TO BE REMOVED:'
        to_remove = old.repos - new.repos
        if to_remove:
            # empty cache and recheck if we really need to delete it
            old._github['repos'] = {}
            to_remove = old.repos - new.repos
        for repo in to_remove:
            self.remove_repo(old, old.get_repo(repo))
            if self.verbose:
                print '    - %s' % repo

        # CREATE TEAMS
        if self.verbose:
            print 'CREATED TEAMS:'
        to_add = new.teams - old.teams
        for team in to_add:
            self.add_team(old, new.get_team(team))
            if self.verbose:
                print '    - %s' % team

        # REMOVE TEAMS
        if self.verbose:
            print 'REMOVED TEAMS:'
        to_remove = old.teams - new.teams
        for team in to_remove:
            self.remove_team(old, old.get_team(team))
            if self.verbose:
                print '    - %s' % team

        if self.verbose:
            print 'UPDATING TEAMS:'
        for team_name in new.teams - to_remove:

            old_team = old.get_team(team_name)
            if old_team is None:
                continue
            new_team = new.get_team(team_name)
            new_team.id = old_team.id

            # UPDATE TEAM PERMISSION
            if new_team.permission != old_team.permission:
                self.edit_team(old, new_team)
                if self.verbose:
                    print '    - %s - UPDATE PERMISSION: %s -> %s' % (
                            old_team.name, old_team.permission, new_team.permission)


            # ADD MEMBERS
            to_add = new_team.members - old_team.members
            if to_add:
                if self.verbose:
                    print '    - %s - ADDED MEMBERS:' % team_name
                for member in to_add:
                    self.add_team_member(old, old_team, member)
                    print '        - %s' % member


            # REMOVE MEMBERS
            to_remove = old_team.members - new_team.members
            if to_remove:
                if self.verbose:
                    print '    - %s - REMOVED MEMBERS:' % team_name
                for member in to_remove:
                    self.remove_team_member(old, old_team, member)
                    print '        - %s' % member

            # ADD REPOS 
            to_add = new_team.repos - old_team.repos
            if to_add:
                if self.verbose:
                    print '    - %s - ADDED REPOS:' % team_name
                for repo in to_add:
                    self.add_team_repo(old, old_team, repo)
                    print '        - %s' % repo

            # REMOVE REPOS
            to_remove = old_team.repos - new_team.repos
            if to_remove:
                if self.verbose:
                    print '    - %s - REMOVED REPOS:' % team_name
                for repo in to_remove:
                    self.remove_team_repo(old, old_team, repo)
                    print '        - %s' % repo

        if self.verbose:
            print 'REQUEST STATS:'
            print '    - request_count: %s' % self.github._request_count
            print '    - request_limit: %s' % self.github._request_limit
            print '    - request_remaining: %s' % self.github._request_remaining

        return True

    #
    # github actions

    def add_repo(self, config, repo):
        config._repos[repo.name] = repo
        return self.github._gh_org_create_repo(repo.name)

    def remove_repo(self, config, repo):
        pass
        #del config._repos[repo.name]
        # TODO: NotImplemented

    def fork_repo(self, config, fork_url, repo):
        config._repos[repo.name] = repo
        return self.github._gh_org_fork_repo(fork_url)

    def add_team(self, config, team):
        config._teams[team.name] = Team(
                name=team.name,
                permission=team.permission,
                )
        response = self.github._gh_org_create_team(
                name=team.name,
                permission=team.permission,
                )
        if response:
            team_dict = json.load(response)
            config._teams[team.name].id = team_dict['id']
        return response

    def edit_team(self, config, team):
        config._teams[team.name].name = team.name
        config._teams[team.name].permission = team.permission
        return self.github._gh_org_edit_team(
                id=team.id,
                name=team.name,
                permission=team.permission,
                )

    def remove_team(self, config, team):
        del config._teams[team.name]
        return self.github._gh_org_delete_team(team.id)

    def add_team_member(self, config, team, member):
        team = config.get_team(team.name)
        team.members.add(member)
        return self.github._gh_org_add_team_member(team.id, member)

    def remove_team_member(self, config, team, member):
        team = config.get_team(team.name)
        team.members.remove(member)
        return self.github._gh_org_remove_team_member(team.id, member)

    def add_team_repo(self, config, team, repo):
        team = config.get_team(team.name)
        team.repos.add(repo)
        return self.github._gh_org_add_team_repo(team.id, repo)

    def remove_team_repo(self, config, team, repo):
        team = config.get_team(team.name)
        team.repos.remove(repo)
        return self.github._gh_org_remove_team_repo(team.id, repo)
