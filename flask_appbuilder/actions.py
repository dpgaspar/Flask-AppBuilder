
class ActionItem(object):
    name = ""
    text = ""
    confirmation = ""
    icon = ""
    multiple = False
    func = None

    def __init__(self, name, text, confirmation, icon, multiple, func):
        self.name = name
        self.text = text
        self.confirmation = confirmation
        self.icon = icon
        self.multiple = multiple
        self.func = func

    def __repr__(self):
        return "Action name:%s; text:%s; func:%s;" % (self.name, self.text, self.func.__name__)


def action(name, text, confirmation=None, icon = None, multiple=False):
    """
        Use this decorator to expose actions

        :param name:
            Action name
        :param text:
            Action text.
        :param confirmation:
            Confirmation text. If not provided, action will be executed
            unconditionally.
        :param icon:
            Font Awesome icon name
    """
    def wrap(f):
        f._action = (name, text, confirmation, icon, multiple)
        return f

    return wrap
