

class Repo(object):

    def __init__(self, name, **kw):
        self.name = name

    def __repr__(self):
        return '<Repo "%s">' % self.name

    def __str__(self):
        return self.__repr__()

    def dumps(self):
        return {
            'name': self.name,
            }
