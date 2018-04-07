sprockets.mixins.correlation
============================

|Version| |Status| |License| |Documentation|

This sprocket provides a single mix-in that imbues your ``RequestHandler``
with a unique correlation ID.  If a correlation ID is present upon input then
it will be preserved in the output.  It is also available for your use as
the ``correlation_id`` property.

Installation
------------

``sprockets.mixins.correlation`` is available on the `Python Package Index`_
and can be installed via ``pip``:

.. code-block:: shell

   $ pip install sprockets.mixins.correlation

Example
-------

.. code-block:: python

   from sprockets.mixins import correlation
   from tornado import ioloop, web

   class Handler(correlation.HandlerMixin, web.RequestHandler):
      def get(self):
         self.finish('my id is {0}'.format(self.correlation_id)

   if __name__ == '__main__':
      application = web.Application([('/', Handler)])
      application.listen(8888)
      ioloop.IOLoop.instance().start()

Generated Correlation ID
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: http

   GET / HTTP/1.1
   Host: localhost:8888
   Connection: keep-alive

.. code-block:: http

   HTTP/1.1 200 OK
   Correlation-ID: 0a2b6080-e4da-43bf-a2a5-38d861846cb9
   Content-Length: 44

   my id is 0a2b6080-e4da-43bf-a2a5-38d861846cb9

Relayed Correlation ID
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: http

   GET / HTTP/1.1
   Host: localhost:8888
   Connection: keep-alive
   Correlation-Id: 4676922073c4c59b1f5e6b4a18894bd46f867316

.. code-block:: http

   HTTP/1.1 200 OK
   Correlation-ID: 4676922073c4c59b1f5e6b4a18894bd46f867316
   Connection: close
   Content-Length: 48

   my id is 4676922073c4c59b1f5e6b4a18894bd46f867316


.. |Version| image:: https://img.shields.io/pypi/v/sprockets.mixins.correlation.svg
   :target: https://pypi.python.org/pypi/sprockets.mixins.correlation
.. |Status| image:: https://img.shields.io/travis/sprockets/sprockets.mixins.correlation.svg
   :target: https://travis-ci.org/sprockets/sprockets.mixins.correlation
.. |Coverage| image:: https://img.shields.io/coveralls/sprockets/sprockets.mixins.correlation.svg
   :target: http://coveralls.io/r/sprockets/sprockets.mixins.correlation
.. |Downloads| image:: https://img.shields.io/pypi/dm/sprockets.mixins.correlation.svg
   :target: https://pypi.python.org/pypi/sprockets.mixins.correlation
.. |License| image:: https://img.shields.io/github/license/sprockets/sprockets.mixins.correlation.svg?
   :target: https://sprocketsmixinscorrelation.readthedocs.io/
.. |Documentation| image:: https://readthedocs.org/projects/sprocketsmixinscorrelation/badge
   :target: https://sprocketsmixinscorrelation.readthedocs.io/

.. _Python Package Index: https://pypi.python.org/pypi/sprockets.mixins.correlation
