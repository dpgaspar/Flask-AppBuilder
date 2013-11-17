
class ActionItem():
    name = ""
    text = ""
    confirmation = ""
    href = ""
    func = None

    def __init__(self, name, text, confirmation, func):
        self.name = name
        self.text = text
        self.confirmation = confirmation
        self.func = func

def action(name, text, confirmation=None):
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
        f._action = (name, text, confirmation)
        return f

    return wrap

