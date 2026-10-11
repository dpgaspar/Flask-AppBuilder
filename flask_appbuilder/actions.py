class ActionItem(object):
    def __init__(
        self, name, text, confirmation, icon, multiple, single, btn_class, func
    ):
        self.name = name
        self.text = text or name
        self.confirmation = confirmation
        self.icon = icon
        self.multiple = multiple
        self.single = single
        self.btn_class = btn_class
        self.func = func

    def __repr__(self):
        return "Action name:%s; text:%s; confirmation:%s; func:%s;" % (
            self.name,
            self.text,
            self.confirmation,
            self.func.__name__,
        )


def action(
    name,
    text,
    confirmation=None,
    icon=None,
    multiple=True,
    single=True,
    btn_class="btn-primary",
):
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
    :param multiple:
        If true will display action on list view
    :param single:
        If true will display action on show view
    :param btn_class:
        Bootstrap button class name. Defaults to btn-primary
    """

    def wrap(f):
        f._action = (name, text, confirmation, icon, multiple, single, btn_class)
        return f

    return wrap
