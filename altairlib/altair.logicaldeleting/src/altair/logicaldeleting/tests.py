import unittest
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlahelper

from . import install
install()

DBSession = sqlahelper.get_session()

session = DBSession

DBSession.remove()

engine = sa.create_engine('sqlite:///')

sqlahelper.add_engine(engine)


Base = sqlahelper.get_base()

class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    deleted_at = sa.Column(sa.DateTime)

class Address(Base):
    __tablename__ = 'addresses'
    id = sa.Column(sa.Integer, primary_key=True)
    deleted_at = sa.Column(sa.DateTime)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    user = orm.relationship('User', backref="addresses")

class Profile(Base):
    __tablename__ = 'profiles'
    id = sa.Column(sa.Integer, primary_key=True)
    deleted_at = sa.Column(sa.DateTime)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    user = orm.relationship('User', backref="profiles")

class ProfilePicture(Base):
    __tablename__ = 'profile_pictures'
    id = sa.Column(sa.Integer, primary_key=True)
    deleted_at = sa.Column(sa.DateTime)
    profile_id = sa.Column(sa.Integer, sa.ForeignKey('profiles.id'))
    profile = orm.relationship('Profile', backref="pictures")


class TestIt(unittest.TestCase): 
    def setUp(self):
        DBSession.remove()
        Base.metadata.create_all(bind=DBSession.bind)

    def tearDown(self):
        DBSession.remove()
        Base.metadata.drop_all(bind=DBSession.bind)

    def test_installed(self):
        from . import LogicalDeletableSession
        isinstance(DBSession(),
                   LogicalDeletableSession)

    def test_normal(self):

        u = User(addresses=[Address()])
        DBSession.add(u)
        DBSession.flush()
        id = u.id
        del u
        import transaction
        transaction.commit()
        DBSession.remove()

        u2 = DBSession.query(User).filter(User.id==id).one()
        
        self.assertEqual(len(u2.addresses), 1)

    def test_logical_delete_address(self):
        from datetime import datetime

        u = User(addresses=[Address(deleted_at=datetime.now())])
        DBSession.add(u)
        DBSession.flush()
        id = u.id
        del u
        import transaction
        transaction.commit()
        DBSession.remove()

        u2 = DBSession.query(User).filter(User.id==id).one()
        
        self.assertEqual(len(u2.addresses), 0)

    def test_logical_delete_address2(self):
        from datetime import datetime

        u = User(addresses=[Address(deleted_at=datetime.now())])
        DBSession.add(u)
        DBSession.flush()
        id = u.id
        del u
        import transaction
        transaction.commit()
        DBSession.remove()

        results = DBSession.query(Address).filter(Address.user_id==User.id).filter(User.id==id).all()
        
        self.assertEqual(results, [])


    def test_including_deleted_address(self):
        from datetime import datetime

        u = User(addresses=[Address(deleted_at=datetime.now())])
        DBSession.add(u)
        DBSession.flush()
        id = u.id
        del u
        import transaction
        transaction.commit()
        DBSession.remove()

        u2 = DBSession.query(User, include_deleted=True).filter(User.id==id).one()
        
        #self.assertEqual(len(u2.addresses), 1)

    def test_complex_1(self):
        from datetime import datetime
        import transaction
        u = User(
            addresses=[
                Address(deleted_at=datetime.now())
                ],
            profiles=[
                Profile(
                    pictures=[
                        ProfilePicture(deleted_at=datetime.now()),
                        ProfilePicture(),
                        ]
                    ),
                ],
            deleted_at=datetime.now()
            )
        DBSession.add(u)
        transaction.commit()
        DBSession.remove()
        q = DBSession.query(User).join(Address).join(Profile).order_by(User.id)
        self.assertEqual([], q.all())

    def test_complex_2(self):
        from datetime import datetime
        from sqlalchemy.orm import joinedload_all
        import transaction
        u = User(
            addresses=[
                Address()
                ],
            profiles=[
                Profile(
                    pictures=[
                        ProfilePicture(deleted_at=datetime.now()),
                        ProfilePicture(),
                        ]
                    ),
                Profile(
                    pictures=[
                        ProfilePicture(deleted_at=datetime.now()),
                        ProfilePicture(),
                        ],
                    deleted_at=datetime.now()
                    ),
                ]
            )
        DBSession.add(u)
        transaction.commit()
        DBSession.remove()
        q = DBSession.query(User) \
            .options(joinedload_all(
                User.profiles,
                Profile.pictures
                )) \
            .join(Address) \
            .order_by(User.id)
        result = q.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0].profiles), 1)
        self.assertEqual(len(result[0].profiles[0].pictures), 1)

    def test_nested(self):
        from datetime import datetime
        from sqlalchemy.orm import joinedload_all
        import transaction
        u = User(
            addresses=[
                Address()
                ],
            profiles=[
                Profile(
                    pictures=[
                        ProfilePicture(deleted_at=datetime.now()),
                        ProfilePicture(),
                        ]
                    ),
                Profile(
                    pictures=[
                        ProfilePicture(deleted_at=datetime.now()),
                        ProfilePicture(),
                        ],
                    deleted_at=datetime.now()
                    ),
                ]
            )
        DBSession.add(u)
        transaction.commit()
        DBSession.remove()
        sq = DBSession.query(User) \
            .options(joinedload_all(
                User.profiles,
                Profile.pictures
                )) \
            .join(Address) \
            .order_by(User.id)
        q = DBSession.query(User).filter(User.id.in_(sq.with_entities(User.id)))
        result = q.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0].profiles), 1)
        self.assertEqual(len(result[0].profiles[0].pictures), 1)

