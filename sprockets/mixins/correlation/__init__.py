try:
    from .mixins import HandlerMixin
except ImportError:

    class HandlerMixin(object):
        def __init__(self, *args, **kwargs):
            raise ImportError


version_info = (3, 0, 0)
__version__ = '.'.join(str(v) for v in version_info[:3])
