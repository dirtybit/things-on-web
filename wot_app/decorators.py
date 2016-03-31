from functools import wraps


def filter_paths(include=None, exclude=None):

    assert include or exclude, "either paths or the exclude param should be provided"

    def class_wrapper(cls):
        def should_skip(path, include=None, exclude=None):
            if include:
                return not any(path.startswith(i) for i in include)

            if exclude:
                return any(path.startswith(e) for e in exclude)

            return True

        @wraps(cls, updated=[])
        class PathFilteredMiddleware(cls):

            def process_request(self, request):
                if should_skip(request.path, include, exclude):
                    return

                if hasattr(cls, 'process_request'):
                    super().proces_request(request)

            def process_response(self, request, response):
                if should_skip(request.path, include, exclude):
                    return response

                if hasattr(cls, 'process_response'):
                    return super().process_response(request, response)
                else:
                    return response

            def process_view(self, request, view, view_args, view_kwargs):
                if should_skip(request.path, include, exclude):
                    return None

                if hasattr(cls, 'process_view'):
                    return super().process_view(request, view, view_args, view_kwargs)
                else:
                    return None

        return PathFilteredMiddleware

    return class_wrapper


def access_controlled():
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            pass
        return _wrapped_view
    return decorator
