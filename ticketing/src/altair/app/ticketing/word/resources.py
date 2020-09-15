# -*- coding:utf-8 -*-

import json

import transaction
from altair.app.ticketing.core.models import Organization
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.users.models import Word
from altair.sqlahelper import get_db_session
from sqlalchemy import desc


class WordBase(TicketingAdminResource):

    def __init__(self, request):
        self.session = get_db_session(request, name="slave")
        super(WordBase, self).__init__(request)


class WordResource(WordBase):

    def __init__(self, request):
        super(WordResource, self).__init__(request)

    def get_words(self):
        query = self.session.query(Word) \
 \
        # if search_form and search_form.label.data:
        #     query = query.filter(ExternalSerialCodeSetting.label.like(u"%{0}%".format(search_form.label.data)))

        query = query.order_by(desc(Word.created_at))
        return query.all()

    def get_master_words(self):
        query = Word.query(Word) \
 \
        # if search_form and search_form.label.data:
        #     query = query.filter(ExternalSerialCodeSetting.label.like(u"%{0}%".format(search_form.label.data)))

        query = query.order_by(desc(Word.created_at))
        return query.all()

    def save_words(self, response):
        organization_id = self.organization.id
        operator_id = self.user.id

        data = response.read()
        json_data = json.loads(data)
        for word_data in json_data['words']:
            word = Word.query.filter(Word.id == word_data['id']).first()
            if not word:
                word = Word()
                word.id = word_data['id']
            word.type = word_data['type']
            word.label = word_data['label']
            word.label_kana = word_data['label_kana']
            word.description = word_data['description']
            word.save()
        transaction.commit()

        self.user = self.get_operator(operator_id)
        self.organization = self.get_organization(organization_id)


    def get_operator(self, operator_id):
        return Operator.query.filter(Operator.id==operator_id).first()

    def get_organization(self, organization_id):
        return Organization.query.filter(Organization.id==organization_id).first()
