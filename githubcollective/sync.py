

class Sync(object):
    """
    """

    __name__ = 'githubcollective-sync'

    def __init__(self, verbose):
        self.verbose = verbose

    def run(self, config, github):
        # REPOS
        to_add = config.repos - github.repos
        to_remove = github.repos - config.repos
        if self.verbose:
            print 'REPOS TO ADD:\n--- ' + ', '.join(to_add)
            print 'REPOS TO REMOVE:\n--- ' + ', '.join(to_remove)
        for repo in to_add:
            # TODO: fork instead of only create repo
            fork_url = config.get_fork_url(repo)
            if fork_url is None:
                github.add_repo(config.get_repo(repo))
            else:
                github.fork_repo(fork_url, config.get_repo(repo))
        for repo in to_remove:
            github.remove_repo(github.get_repo(repo))

        # TEAMS
        to_add = config.teams - github.teams
        to_remove = github.teams - config.teams
        if self.verbose:
            print 'TEAMS TO ADD:\n--- ' + ', '.join(to_add)
            print 'TEAMS TO REMOVE:\n--- ' + ', '.join(to_remove)
        for team in to_add:
            github.add_team(config.get_team(team))
        for team in to_remove:
            github.remove_team(github.get_team(team))


        # UPDATE TEAMS
        if self.verbose:
            print 'TEAMS TO UPDATE:'
        for team_name in config.teams-to_remove:
            team = github.get_team(team_name)
            config_team = config.get_team(team_name)
            config_team.id = team.id
            if team is None:
                continue
            if self.verbose:
                print '--- %s:' % team.name

            # UPDATE PERMISSION
            if config_team.permission != team.permission:
                if self.verbose:
                    print '------- UPDATE PERMISSION: %s -> %s' % (
                            team.permission, config_team.permission)
                github.edit_team(config_team)


            # UPDATE MEMBERS
            to_add = set(config_team.members) - set(team.members)
            to_remove = set(team.members) - set(config_team.members)
            if self.verbose:
                print '------- MEMBERS TO ADD: %s' % ', '.join(to_add)
                print '------- MEMBERS TO REMOVE: %s' % ', '.join(to_remove)
            for member in to_add:
                github.add_team_member(team, member)
            for member in to_remove:
                github.remove_team_member(team, member)

            # UPDATE REPOS 
            to_add = config_team.repos - team.repos
            to_remove = team.repos - config_team.repos
            if self.verbose:
                print '------- REPOS TO ADD: %s' % ', '.join(to_add)
                print '------- REPOS TO REMOVE: %s' % ', '.join(to_remove)
            for repo in to_add:
                github.add_team_repo(team, repo)
            for repo in to_remove:
                github.remove_team_repo(team, repo)

        if self.verbose:
            print 'REQUEST STATS:'
            print '--- request_count: %s' % github._request_count
            print '--- request_limit: %s' % github._request_limit
            print '--- request_remaining: %s' % github._request_remaining

        return True
