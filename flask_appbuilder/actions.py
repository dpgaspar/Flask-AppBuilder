
class ActionItem():
    name = ""
    text = ""
    confirmation = ""
    href = ""
    func = None

    def __init__(self, name, text, confirmation, icon, func):
        self.name = name
        self.text = text
        self.confirmation = confirmation
        self.func = func

    def __repr__(self):
        return "Action name:%s; text:%s; func:%s;" % (self.name, self.text, self.func.__name__)

def action(name, text, confirmation=None, icon = None):
    """
        Use this decorator to expose actions

        :param name:
            Action name
        :param text:
            Action text.
        :param confirmation:
            Confirmation text. If not provided, action will be executed
            unconditionally.
    """
    def wrap(f):
        f._action = (name, text, confirmation, icon)
        return f

    return wrap
