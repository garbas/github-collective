

class Team(object):

    def __init__(self, name, permission, id=None,
            members_count=0, repos_count=0,
            members=[], repos=[],
            **kw
            ):
        self.id = id
        self.name = name
        self.permission = permission
        self.members_count = members_count
        self.repos_count = repos_count
        self.members = set(members)
        self.repos = set(repos)

    def __repr__(self):
        return '<Team at %s:"%s">' % (self.id, self.name)

    def __str__(self):
        return self.__repr__()
