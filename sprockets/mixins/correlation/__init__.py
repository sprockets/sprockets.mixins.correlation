try:
    from .mixins import CorrelationAdapter, HandlerMixin, LoggingMixin

# the following makes importing the module possible when tornado
# is not installed in the active environment
except ImportError as exc:  # pragma no cover
    def CorrelationAdapter(*args, **kwargs):
        raise exc

    def HandlerMixin(*args, **kwargs):
        raise exc

    def LoggingMixin(*args, **kwargs):
        raise exc


version_info = (1, 1, 0)
__version__ = '.'.join(str(v) for v in version_info[:3])
