import unittest
import mock
from pyramid import testing


class SessionSeparationTest(unittest.TestCase):
    def dummy_setting_factory(self, override_name, organization_id):
        return testing.DummyModel(
            shop_name=u'shop_name',
            shop_id=u'shop_id',
            auth_id=u'auth_id',
            auth_password=u'auth_password'
            )
    
    def setUp(self):
        import sqlalchemy as sa
        from sqlalchemy.orm import ScopedSession, sessionmaker
        from ..testing import DummyCheckout3D
        import sqlahelper
        import tempfile

        self.tmpfile = tempfile.mkstemp()
        engine = sa.create_engine("sqlite:///%s" % self.tmpfile[1])
        sqlahelper.add_engine(engine)
        self.main_session = ScopedSession(sessionmaker())
        self.main_session.configure(bind=engine)

        self.config = testing.setUp(settings={
            'altair.multicheckout.endpoint.base_url': 'example.com',
            'altair.multicheckout.endpoint.timeout': 10,
            })
        self.config.include('altair.multicheckout')
        self.config.set_multicheckout_setting_factory(self.dummy_setting_factory)
        class TestModel(sqlahelper.get_base()):
            __tablename__ = __name__.replace('.', '_')
            id = sa.Column(sa.Integer(), primary_key=True, nullable=False)

        from .. import models
        sqlahelper.get_base().metadata.create_all()
        self.test_model = TestModel

    def tearDown(self):
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()
        testing.tearDown()

    @mock.patch('altair.multicheckout.impl.Checkout3D')
    def test_it(self, impl):
        from altair.multicheckout.models import _session, MultiCheckoutResponseCard
        from altair.multicheckout.api import get_multicheckout_3d_api
        request = testing.DummyRequest
        model = self.test_model(id=1)
        self.main_session.add(model)
        impl.return_value.request_card_cancel_sales.return_value = MultiCheckoutResponseCard()
        multicheckout_api = get_multicheckout_3d_api(testing.DummyRequest())
        multicheckout_api.checkout_sales_cancel(u'XX0000000000')

        self.assertEqual(1, len(self.main_session.query(MultiCheckoutResponseCard).all()))
        self.assertEqual(0, len(_session.query(self.test_model).filter_by(id=1).all()))
        self.main_session.commit()
        self.assertEqual(1, len(_session.query(self.test_model).filter_by(id=1).all()))

