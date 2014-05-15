

class BaseManager(object):
    """
        The parent class for all Managers
    """
    def __init__(self, appbuilder):
        self.appbuilder = appbuilder

    def register_views(self):
        pass
