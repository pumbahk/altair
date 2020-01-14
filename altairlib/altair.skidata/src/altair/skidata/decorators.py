import inspect
import re

from lxml import etree

from altair.skidata.utils import marshal_skidata_xml_model, unmarshal_skidata_xml, ALLOWED_ITERABLE_TYPES, \
    is_skidata_xml_context

SKIDATA_XML_CONTEXT_FUNC = 'skidata_xml_context_func'


class SkidataXmlBaseContext(object):
    """Base class to represent Skidata XML context"""
    def __init__(self, func=None, name=None, required=True, data_type=None, maxlength=None):
        # a function is given when this object wraps a function with no argument.
        self._func = func

        # an XML context name
        self._name = name

        # boolean if an XML context is mandatory or optional
        self._required = required

        # SkidataDataType object to define Skidata XML data type
        from altair.skidata.models import SkidataDataType
        self._data_type = data_type if isinstance(data_type, SkidataDataType) else SkidataDataType.STRING

        # a maximum length of an XML context value
        if maxlength is not None and maxlength <= 0:
            raise ValueError('maxlength ({}) is not a positive integer'.format(maxlength))
        self._maxlength = maxlength

    def __get__(self, instance, owner):
        """Called to get the attributes of this class when no argument is given."""
        return self.__call__(self._func, instance)

    def __call__(self, wrapped, instance=None):
        # Accept when the decorator wraps a function
        if not inspect.isfunction(wrapped):
            return wrapped

        def wrapper(*args, **kwargs):
            """A function which is called instead of the function skidata_property wraps."""
            obj = args[0] if len(args) > 0 else instance

            # A base name is what follows `get_`
            base_name = re.sub(r'^get_', '', wrapped.func_name)

            # Marshal an object with __marshalling__ attribute set to `normal` or `strict`
            # to an XML Element object (represented by lxml.etree.Element)
            #
            # Marshaled value is cut off at the maximum length in `strict` mode.
            #
            marshal_mode = getattr(obj, '__marshalling__', None)
            if marshal_mode in ('normal', 'strict'):
                marshaller = getattr(obj, 'marshal_{}'.format(base_name), None)
                w_res = wrapped(obj) if marshaller is None else marshaller()
                return self._marshal(obj, w_res, self._xml_name(base_name), marshal_mode == 'strict')

            # Unmarshal an XML Element object (represented by lxml.etree.Element)
            # in __unmarshalling__ attribute to an object
            xml = getattr(obj, '__unmarshalling__', None)
            if etree.iselement(xml):
                # A setter function name is a combination with a prefix 'set_' and a base name
                setter = getattr(obj, 'set_{}'.format(base_name), None)
                # A setter function is used as a default unmarshaller function
                unmarshaller = getattr(obj, 'unmarshal_{}'.format(base_name), setter)

                value = self._target_to_unmarshal(obj, xml, base_name)
                if unmarshaller is not None and value is not None:
                    self._unmarshal(unmarshaller, value, wrapped(obj))
                return

            # Call a function the decorator wraps
            return wrapped(obj, **kwargs)

        wrapper.__name__ = SKIDATA_XML_CONTEXT_FUNC
        return wrapper

    def _xml_name(self, base_name):
        """Return an XML data name.
        Return the string obtained by replacing
        the occurrences of underscore and lowercase in base_name by uppercase
        and making the first character capitalized when _name is NoneType or empty
        """
        if not self._name:
            repled = re.sub(r'_([a-z])', lambda m: m.group(1).upper(), base_name)
            return re.sub(r'^([a-z])', lambda m: m.group(1).upper(), repled)

        return self._name

    def _target_to_unmarshal(self, obj, xml, basename):
        pass

    def _marshal(self, obj, value, xml_name, strict):
        pass

    def _unmarshal(self, unmarshaller, value, existing_value):
        pass


class SkidataXmlElement(SkidataXmlBaseContext):
    """A decorator to represent the Skidata XML Element"""
    def __init__(self, func=None, name=None, namespace=None, required=True,
                 data_type=None, multi=False, cls=None, maxlength=None):
        """
        class C(object):
            def __init__(self, x):
                self._x = x

            @SkidataXmlElement
            def x(self):
                return self._x

            def set_x(self, value):
                self._x = value

        > c = C(x='test')

        from altair.skidata.marshaller import SkidataXmlMarshaller
        SkidataXmlMarshaller.marshal(c)
        > '<C><X>test</X></C>'

        from altair.skidata.unmarshaller import SkidataXmlUnmarshaller
        SkidataXmlUnmarshaller.unmarshal('<C><X>test</X></C>', C)
        > C(x='test')

        ------------------
        SkidataXmlElement also wraps a class, which works
        when a wrapping class is handled as a root element.
        A function name of which starts with `marshal_` and `unmarshal_` are called
        instead when marshalling and unmarshalling respectively.

        > from datetime import date, datetime

        @SkidataXmlElement(name='CC')
        class C(object):
            def __init__(self, x):
                self._x = x

            @SkidataXmlElement
            def x(self):
                return self._x

            def marshal_x(self):
                return self._x.strftime('%d/%m/%Y')

            def unmarshal_x(self, value):
                self._x = datetime.strptime(value, '%d/%m/%Y').date()

        > c = C(x=date(2020, 1, 1))

        from altair.skidata.marshaller import SkidataXmlMarshaller
        SkidataXmlMarshaller.marshal(c)
        > '<CC><X>01/01/2020</X></CC>'

        from altair.skidata.unmarshaller import SkidataXmlUnmarshaller
        SkidataXmlUnmarshaller.unmarshal('<CC><X>01/01/2020</X></CC>', C)
        > C(x=date(2020, 1, 1))
        """
        # an XML namespace mapping
        self._nsmap = {None: str(namespace)} if namespace is not None else None

        # boolean to marshal an iterable object in the same node if true
        # an iterable object needs to contain class object(s) whose class is the same as cls value
        self._multi = multi

        element_name = name
        # Class type with which a object is instantiated when unmarshaled
        if cls is not None:
            if not (inspect.isclass(cls) and inspect.ismethod(getattr(cls, '__init__', None))):
                raise TypeError('cls ({}) is not a class type with __init__ function'.format(cls))
            # Use an class name as an XML Element name
            if not element_name:
                element_name = cls.__name__
        self._cls = cls

        super(SkidataXmlElement, self).__init__(func=func, name=element_name, required=required,
                                                data_type=data_type, maxlength=maxlength)

    def __call__(self, wrapped, instance=None):
        if inspect.isfunction(wrapped):
            return super(SkidataXmlElement, self).__call__(wrapped, instance)

        if inspect.isclass(wrapped):
            # Set __marshal__ method when the decorator wraps a class
            # The method marshals a class to an XML Element object (represented by lxml.etree.Element)
            setattr(wrapped, '__marshal__',
                    lambda _: etree.Element(self._name or wrapped.__name__, nsmap=self._nsmap))

        # Call a function the decorator wraps
        return wrapped

    def _target_to_unmarshal(self, obj, xml, basename):
        """
        An XML Element name is expected to be the same as the counterpart
        derived from an object with a function this decorator wraps.
        """
        if etree.QName(xml).localname == self._xml_name(basename):
            return xml
        return None

    def _marshal(self, obj, value, xml_name, strict):
        element = None
        if getattr(value, '__class__', None) is self._cls:
            element = etree.Element(xml_name, nsmap=self._nsmap)
            marshal_skidata_xml_model(value, element, strict=strict)
        elif self._multi:
            if isinstance(value, ALLOWED_ITERABLE_TYPES):
                return self._marshal_iterable(value, xml_name, strict)
        elif self._cls is not None and not self._required:
            return None
        elif self._required or (not self._required and value is not None):
            element = etree.Element(xml_name, nsmap=self._nsmap)

            text_value = self._data_type.format(value)
            if isinstance(self._maxlength, int) and strict:
                text_value = text_value[0:self._maxlength]
            element.text = text_value
        return element

    def _marshal_iterable(self, iterable, xml_name, strict):
        """
        Iterate an iterable object and append the elements to an XML element.
        :param iterable: an iterable object
        """
        elements = []
        for obj in iterable:
            if getattr(obj, '__class__', None) is not self._cls:
                continue
            element = etree.Element(xml_name, nsmap=self._nsmap)
            marshal_skidata_xml_model(obj, element, strict=strict)
            elements.append(element)
        return elements

    def _unmarshal(self, unmarshaller, value, existing_value):
        if self._cls is not None:
            init_args = (None,) * (len(inspect.getargspec(self._cls.__init__).args) - 1)
            inner_obj = self._cls(*init_args)

            # Set __element_name__ attribute to record an unmarshalling XML Element name
            setattr(inner_obj, '__element_name__', self._xml_name(self._cls.__name__))

            unmarshal_skidata_xml(value, inner_obj)
            unmarshaller(self._yield_value(inner_obj, existing_value))
        else:
            parsed = self._data_type.parse(value.text)
            unmarshaller(self._yield_value(parsed, existing_value))

    def _yield_value(self, new_value, existing_value):
        if self._multi and existing_value is not None:
            if isinstance(existing_value, ALLOWED_ITERABLE_TYPES):
                return list(existing_value) + [new_value]
            else:
                return [existing_value, new_value]
        else:
            return new_value


class SkidataXmlAttribute(SkidataXmlBaseContext):
    """A decorator to represent the Skidata XML Attribute"""
    def __init__(self, func=None, name=None, namespace=None, required=True, data_type=None, maxlength=None):
        """
        class C(object):
            def __init__(self, x):
                self._x = x

            @SkidataXmlAttribute
            def x(self):
                return self._x

            def set_x(self, value):
                self._x = value

        > c = C(x='test')

        from altair.skidata.marshaller import SkidataXmlMarshaller
        SkidataXmlMarshaller.marshal(c)
        > <C X="test"/>

        from altair.skidata.unmarshaller import SkidataXmlUnmarshaller
        SkidataXmlUnmarshaller.unmarshal('<C X="test"/>', C)
        > C(x='test')

        ------------------
        A function name of which starts with `marshal_` and `unmarshal_` are called
        instead when marshalling and unmarshalling respectively.

        > from datetime import date, datetime

        class C(object):
            def __init__(self, x):
                self._x = x

            @SkidataXmlAttribute
            def x(self):
                return self._x

            def marshal_x(self):
                return self._x.strftime('%d/%m/%Y')

            def unmarshal_x(self, value):
                self._x = datetime.strptime(value, '%d/%m/%Y').date()

        > c = C(x=date(2020, 1, 1))

        from altair.skidata.marshaller import SkidataXmlMarshaller
        SkidataXmlMarshaller.marshal(c)
        > '<C X="01/01/2020"/>'

        from altair.skidata.unmarshaller import SkidataXmlUnmarshaller
        SkidataXmlUnmarshaller.unmarshal('<C X="01/01/2020"/>', C)
        > C(x=date(2020, 1, 1))
        """
        # an XML namespace
        self._namespace = namespace if namespace is not None else ''

        super(SkidataXmlAttribute, self).__init__(func=func, name=name, required=required,
                                                  data_type=data_type, maxlength=maxlength)

    def _target_to_unmarshal(self, obj, xml, basename):
        """
        An XML Attribute is expected to belong to an XML Element
        whose name is corresponding to that of the unmarshalling element.
        """
        element_name = getattr(obj, '__element_name__', obj.__class__.__name__)
        if etree.QName(xml).localname == element_name:
            attrib_name = self._xml_name(basename)
            if self._namespace is not None:
                attrib_name = '{{{namespace}}}{name}'.format(namespace=self._namespace,
                                                             name=attrib_name)
            return xml.get(attrib_name)
        return None

    def _marshal(self, obj, value, xml_name, strict):
        attrib_val = self._data_type.format(value)
        if isinstance(self._maxlength, int) and strict:
            attrib_val = attrib_val[0:self._maxlength]

        # An XML attribute is optional and has no value.
        if not self._required and not attrib_val:
            return None

        attrib_key = '{{{namespace}}}{name}'.format(namespace=self._namespace, name=xml_name)
        # Return a dict (key: attribute name including namespace, value: attribute value)
        return {'key': attrib_key, 'value': attrib_val}

    def _unmarshal(self, unmarshaller, value, existing_value):
        unmarshaller(self._data_type.parse(value))


class SkidataXmlElementOrder(object):
    """A decorator to arrange XML Elements in func_names order. """
    def __init__(self, func_names):
        # a list of function names wrapped by SkidataXmlElement
        self._func_names = func_names

    def __call__(self, wrapped):
        if not isinstance(self._func_names, list):
            self._func_names = []

        def func_order(obj):
            funcs = []
            for func_name in self._func_names:
                func = getattr(obj, func_name, None)
                if is_skidata_xml_context(func):
                    funcs.append(func)
            return funcs

        if inspect.isclass(wrapped):
            setattr(wrapped, '__skidata_xml_element_order__', func_order)
        return wrapped
