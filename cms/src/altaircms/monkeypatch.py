from pyramid.path import caller_package

"""
monkey patching.
"""


def config_scan_patch():
    """
    this patch is enable to use ignore keywords arguments in Configurator#scan()
    (for ignore test modules)

    this is new as Venusian 1.0a3
    http://docs.pylonsproject.org/projects/venusian/en/latest/
    """
    from  pyramid.config import Configurator

    def scan(self, package=None, categories=None, onerror=None, ignore=None, **kw):
        """Scan a Python package and any of its subpackages for objects
        marked with :term:`configuration decoration` such as
        :class:`pyramid.view.view_config`.  Any decorated object found will
        influence the current configuration state.

        The ``package`` argument should be a Python :term:`package` or module
        object (or a :term:`dotted Python name` which refers to such a
        package or module).  If ``package`` is ``None``, the package of the
        *caller* is used.

        The ``categories`` argument, if provided, should be the
        :term:`Venusian` 'scan categories' to use during scanning.  Providing
        this argument is not often necessary; specifying scan categories is
        an extremely advanced usage.  By default, ``categories`` is ``None``
        which will execute *all* Venusian decorator callbacks including
        :app:`Pyramid`-related decorators such as
        :class:`pyramid.view.view_config`.  See the :term:`Venusian`
        documentation for more information about limiting a scan by using an
        explicit set of categories.

        The ``onerror`` argument, if provided, should be a Venusian
        ``onerror`` callback function.  The onerror function is passed to
        :meth:`venusian.Scanner.scan` to influence error behavior when an
        exception is raised during the scanning process.  See the
        :term:`Venusian` documentation for more information about ``onerror``
        callbacks.

        To perform a ``scan``, Pyramid creates a Venusian ``Scanner`` object.
        The ``kw`` argument represents a set of keywords arguments to pass to
        the Venusian ``Scanner`` object's constructor.  See the
        :term:`venusian` documentation (its ``Scanner`` class) for more
        information about the constructor.  By default, the only keywords
        arguments passed to the Scanner constructor are ``{'config':self}``
        where ``self`` is this configurator object.  This services the
        requirement of all built-in Pyramid decorators, but extension systems
        may require additional arguments.  Providing this argument is not
        often necessary; it's an advanced usage.

        .. note:: the ``**kw`` argument is new in Pyramid 1.1
        """
        package = self.maybe_dotted(package)
        if package is None: # pragma: no cover
            package = caller_package()

        ctorkw = {'config':self}
        ctorkw.update(kw)

        scanner = self.venusian.Scanner(**ctorkw)
        scanner.scan(package, categories=categories, onerror=onerror, ignore=ignore)

    Configurator.scan = scan
