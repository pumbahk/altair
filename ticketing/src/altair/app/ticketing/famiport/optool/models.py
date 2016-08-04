# encoding: utf-8

import sqlalchemy as sa
from altair.models import Identifier, WithTimestamp
from ..models import Base
from datetime import datetime, timedelta
from .utils import encrypt_password

class FamiPortOperator(Base, WithTimestamp):
    __tablename__ = 'FamiPortOperator'

    time_now = datetime.now()
    expired_time = time_now + timedelta(days=180)

    id = sa.Column(Identifier, primary_key=True, nullable=False, autoincrement=True)
    user_name = sa.Column(sa.Unicode(32), nullable=False, unique=True)
    password = sa.Column(sa.Unicode(96), nullable=False)
    role = sa.Column(sa.Unicode(32), nullable=False)
    email = sa.Column(sa.Unicode(120), nullable=False, unique=True)
    expired_at = sa.Column(sa.DateTime, default=expired_time, onupdate=expired_time, nullable=True)
    active = sa.Column(sa.Boolean)

    @property
    def has_perm_for_personal_info(self):
        if self.role not in ('administrator', 'superuser',):
            return False
        return True

    @property
    def is_first(self):
        return not self.active

    @property
    def is_expired(self):
        if not self.expired_at:
            return False
        return datetime.now() > self.expired_at

    @property
    def is_deactivated(self):
        if not self.expired_at:
            return False
        return datetime.now() - self.expired_at > timedelta(days=30)

    def is_valid_email(self, email_to_check):
        return self.email == email_to_check

    def is_matched_password(self, password_to_check):
        encrypted_password = encrypt_password(password_to_check, self.password)
        return encrypted_password == self.password
