
class ActionItem():
    name = ""
    text = ""
    func = None

    def __init__(self, name, text, func):
        self.name = name
        self.text = text
        self.func = func

def action(name, text, confirmation=None):
    """
        Use this decorator to expose actions that span more than one
        entity (model, file, etc)

        :param name:
            Action name
        :param text:
            Action text.
        :param confirmation:
            Confirmation text. If not provided, action will be executed
            unconditionally.
    """
    def wrap(f):
        f._action = (name, text, confirmation)
        return f

    return wrap
