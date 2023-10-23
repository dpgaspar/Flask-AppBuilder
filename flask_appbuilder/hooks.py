from typing import Any, Callable, Dict, List


def before_request(
    hook: Callable[[], Any] = None, only: List[str] = None
) -> Callable[..., Any]:
    """
    This decorator provides a way to hook into the request
    lifecycle by enqueueing methods to be invoked before
    each handler in the view. If the method returns a value
    other than :code:`None`, then that value will be returned
    to the client. If invoked with the :code:`only` kwarg,
    the hook will only be invoked for the given list of
    handler methods.

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

    :param hook:
        A callable to be invoked before handlers in the class. If the
        hook returns :code:`None`, then the request proceeds and the
        handler is invoked. If it returns something other than :code:`None`,
        then execution halts and that value is returned to the client.
    :param only:
        An optional list of the names of handler methods. If present,
        :code:`hook` will only be invoked before the handlers specified
        in the list. If absent, :code:`hook` will be invoked for before
        all handlers in the class.
    """

    def wrap(hook: Callable[[], Any]) -> Callable[[], Any]:
        hook._before_request_hook = True
        hook._before_request_only = only
        return hook

    return wrap if hook is None else wrap(hook)


def wrap_route_handler_with_hooks(
    handler_name: str,
    handler: Callable[..., Any],
    before_request_hooks: List[Callable[[], Any]],
) -> Callable[..., Any]:
    applicable_hooks = []
    for hook in before_request_hooks:
        only = hook._before_request_only
        applicable_hook = only is None or handler_name in only
        if applicable_hook:
            applicable_hooks.append(hook)

    if not applicable_hooks:
        return handler

    def wrapped_handler(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        for hook in applicable_hooks:
            result = hook()
            if result is not None:
                return result
        return handler(*args, **kwargs)

    return wrapped_handler


def get_before_request_hooks(view_or_api_instance: Any) -> List[Callable[[], Any]]:
    before_request_hooks = []
    for attr_name in dir(view_or_api_instance):
        attr = getattr(view_or_api_instance, attr_name)
        if hasattr(attr, "_before_request_hook") and attr._before_request_hook is True:
            before_request_hooks.append(attr)
    return before_request_hooks
