try:
    from .mixins import HandlerMixin

except ImportError as error:

    class HandlerMixin(object):
        def __init__(self, *args, **kwargs):
            raise error


version_info = (1, 0, 2)
__version__ = '.'.join(str(v) for v in version_info[:3])
