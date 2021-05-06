def before_request(*args, **kwargs):
    """
        Use this decorator to enqueue methods to be invoked
        before each handler in the view. If method returns
        a value other than :code:`None`, then that value
        will be returned to the client. If invoked with the
        :code:`only` kwarg, the hook will only be invoked for
        the given list of handler methods.

        Examples::

            class MyFeature(ModelView)

                @before_request
                def ensure_feature_is_enabled(self):
                    if self.feature_is_disabled:
                        return self.response_404()
                    return None

                # etc...


            class MyView(ModelRestAPI):

                @before_request(only=["create", "update", "delete"])
                def ensure_write_mode_enabled(self):
                    if self.read_only:
                        return self.response_400()
                    return None

                # etc...


        :param kwargs:
            The :code:`only` kwarg scopes the method being decorated
            to run only for the given list of handler methods. If
            abset, the method will be invoked before all handlers.
    """
    only = kwargs.get("only", None)

    def wrap(f):
        f._before_request_hook = True
        f._before_request_only = only
        return f

    return wrap(args[0]) if len(args) == 1 else wrap


def wrap_route_handler_with_hooks(handler_name, handler, before_request_hooks):
    applicable_hooks = []
    for hook in before_request_hooks:
        only = hook._before_request_only
        applicable_hook = only is None or handler_name in only
        if applicable_hook:
            applicable_hooks.append(hook)

    if not applicable_hooks:
        return handler

    def wrapped_handler(*args, **kwargs):
        for hook in applicable_hooks:
            result = hook()
            if result is not None:
                return result
        return handler(*args, **kwargs)

    return wrapped_handler


def get_before_request_hooks(view_or_api_instance):
    before_request_hooks = []
    for attr_name in dir(view_or_api_instance):
        attr = getattr(view_or_api_instance, attr_name)
        if hasattr(attr, "_before_request_hook") and attr._before_request_hook is True:
            before_request_hooks.append(attr)
    return before_request_hooks
