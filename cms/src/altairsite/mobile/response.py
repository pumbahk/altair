# -*- encoding:utf-8 -*-
def convert_response_for_mobile(response):
    encoding = 'Shift_JIS'
    if response.content_type.startswith("text"):
        response.body = response.unicode_body.encode("cp932", "replace")
        response.content_type = 'application/xhtml+xml; charset=%s' % encoding
    return response

"""
emoziを使い始めたらemojiのmappingテーブルも必要(from django-bpmobile)
"""

