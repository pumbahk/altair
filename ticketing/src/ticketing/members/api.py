# -*- coding:utf-8 -*-

import ticketing.csvutils as csv
from .builder import UserForLoginCartBuilder
import logging
logger = logging.getLogger(__name__)

def edit_membergroup(members, member_group_id):
    members.update({"membergroup_id": member_group_id}, synchronize_session="fetch")

    
def members_import_from_csv(request, io, encoding="cp932"):
    """ <Membergroup>, <loginId>, <Password>を期待
    """
    reader = csv.reader(io, quotechar="'", encoding=encoding)
    builder = UserForLoginCartBuilder(request)
    for membergroup_name, loginname, password in reader:
        builder.build_user_for_login_cart_add_session(
            membergroup_name, 
            loginname,
            password)
    logger.debug("*csv import*: "+str(builder.users))
    return builder.users

def members_export_as_csv(request, io, users, encoding="cp932"):
    """ <Membergroup>, <loginId>, <Password>で出力
    """
    writer = csv.writer(io, quotechar="'", encoding=encoding)
    for row in _member_info_triples(users):
        writer.writerow(row)
    logger.debug("*csv export*: "+str(users))
    io.seek(0)
    return io
    
def _member_info_triples(users):
    for u in users:
        c = u.first_user_credential
        yield u.member.membergroup.name, c.auth_identifier, c.auth_secret
