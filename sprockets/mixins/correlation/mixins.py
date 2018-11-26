import uuid

from tornado import concurrent, log


class HandlerMixin(object):
    """
    Mix this in over a ``RequestHandler`` for a correlating header.

    :keyword str correlation_header: the name of the header to use
        for correlation.  If this keyword is omitted, then the header
        is named ``Correlation-ID``.

    This mix-in ensures that responses include a header that correlates
    requests and responses.  If there header is set on the incoming
    request, then it will be copied to the outgoing response.  Otherwise,
    a new UUIDv4 will be generated and inserted.  The value can be
    examined or modified via the ``correlation_id`` property.

    The MRO needs to contain something that resembles a standard
    :class:`tornado.web.RequestHandler`.  Specifically, we need the
    following things to be available:

    - :meth:`~tornado.web.RequestHandler.prepare` needs to be called
      appropriately
    - :meth:`~tornado.web.RequestHandler.set_header` needs to exist in
      the MRO and it needs to overwrite the header value
    - :meth:`~tornado.web.RequestHandler.set_default_headers` should be
      called to establish the default header values
    - ``self.request`` is a object that has a ``headers`` property that
      contains the request headers as a ``dict``.

    """

    def __init__(self, *args, **kwargs):
        # correlation_id is used from within set_default_headers
        # which is called from within super().__init__() so we need
        # to make sure that it is set *BEFORE* we call super.
        self.__header_name = kwargs.pop(
            'correlation_header', 'Correlation-ID')
        self.__correlation_id = str(uuid.uuid4())
        super(HandlerMixin, self).__init__(*args, **kwargs)

    async def prepare(self):
        # Here we want to copy an incoming Correlation-ID header if
        # one exists.  We also want to set it in the outgoing response
        # which the property setter does for us.
        maybe_future = super(HandlerMixin, self).prepare()
        if concurrent.is_future(maybe_future):
            await maybe_future

        correlation_id = self.get_request_header(self.__header_name, None)
        if correlation_id is not None:
            self.correlation_id = correlation_id

    def set_default_headers(self):
        # This is called during initialization as well as *AFTER*
        # calling clear() when an error occurs so we need to make
        # sure that our header is set again...
        super(HandlerMixin, self).set_default_headers()
        self.set_header(self.__header_name, self.correlation_id)

    @property
    def correlation_id(self):
        """Correlation header value."""
        return self.__correlation_id

    @correlation_id.setter
    def correlation_id(self, value):
        self.__correlation_id = value
        self.set_header(self.__header_name, self.__correlation_id)

    def get_request_header(self, name, default):
        """
        Retrieve the value of a request header.

        :param str name: the name of the header to retrieve
        :param default: the value to return if the header is not set

        This method abstracts the act of retrieving a header value out
        from the implementation.  This makes it possible to implement
        a *RequestHandler* that is something other than a
        :class:`tornado.web.RequestHandler` by simply implementing this
        method and ``set_header`` over the underlying implementation,
        for example, say AMQP message properties.

        """
        return self.request.headers.get(name, default)


def correlation_id_logger(handler):
    """ Custom Tornado access log writer that appends correlation-id.

    This function can be used to append the coorelation-id to the
    Tornado access logs. To use, simply set the value of the
    log_function kwarg of the Tornado Application constructor to this
    function.

    *Example*
    web.Application([], log_function=correlation_id_logger)

    :param tornado.web.RequestHandler handler: the request handler that
        is processing the client request.
    """
    if handler.get_status() < 400:
        log_method = log.access_log.info
    elif handler.get_status() < 500:
        log_method = log.access_log.warning
    else:
        log_method = log.access_log.error
    request_time = 1000.0 * handler.request.request_time()
    correlation_id = getattr(handler, "correlation_id", None)
    if correlation_id is None:
        correlation_id = handler.request.headers.get('Correlation-ID', None)
    log_method("%d %s %.2fms {CID %s}", handler.get_status(),
               handler._request_summary(), request_time, correlation_id)
