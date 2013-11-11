import os

def messages_path():
    """
    Determine the path to the 'messages' directory as best possible.
    """
    module_path = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(module_path), 'messages')


def get_builtin_gnu_translations(languages=None):
    """
    Get a gettext.GNUTranslations object pointing at the
    included translation files.

    :param languages:
        A list of languages to try, in order. If omitted or None, then
        gettext will try to use locale information from the environment.
    """
    import gettext
    return gettext.translation('wtforms', messages_path(), languages)


def get_translations(languages=None):
    """
    Get a WTForms translation object which wraps the builtin GNUTranslations object.
    """
    translations = get_builtin_gnu_translations(languages)

    if hasattr(translations, 'ugettext'):
        return DefaultTranslations(translations)
    else:
        # Python 3 has no ugettext/ungettext, so just return the translations object.
        return translations


class DefaultTranslations(object):
    """
    A WTForms translations object to wrap translations objects which use
    ugettext/ungettext.
    """
    def __init__(self, translations):
        self.translations = translations

    def gettext(self, string):
        return self.translations.ugettext(string)

    def ngettext(self, singular, plural, n):
        return self.translations.ungettext(singular, plural, n)
