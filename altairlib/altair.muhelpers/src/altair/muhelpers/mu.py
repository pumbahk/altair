# cencoding: utf-8

import re
import json
import zipfile
import io

__all__ = [
    'Mailer',
    ]

class Receipient(object):
    def __init__(self, open_id, attributes):
        self.open_id = open_id
        self.attributes = attributes

# TODO: for SPEC
# muhelpers側では、ユーザの氏名は取得できないので、
# attribute 1固定とする、等の決めが必要

class Mailer(object):
    def __init__(self):
        # Mu sepc
        self.field_separater = "_M#8"
        self.line_end = "\n"
        self.line_end_macro = "###_BR_###"
        self.attr_separater = "|"
        self.attribute_macro = "###_ATTRIBUTE%d_###"

        # our spec
        self.macro_pattern = "@@(\w+)@@"
        self.macro_pattern_internal = "\w+"

        # config
        self.attribute_keys = [ ]

    def set_attributes(self, attributes):
        pattern = re.compile(self.macro_pattern_internal)
        for a in attributes:
            if not pattern.match(a):
                raise Exception("%s is not suitable for template macro" % a)

        self.attribute_keys = attributes

    def create_config(self, start_time):
        config = {
            "InputEncode": "UTF-8",
            "RequestEncode": "UTF-8",
            "SendStartTime": start_time.strftime("%Y%m%d%H%M%S")
        }

        return json.dumps(config)

        # ini version
        # return "".join(["%s=%s" % (k, v) for k, v in config ])

    # FIXME: use iterator and stream for large data?
    def create_list(self, receipients):
        def escape(s):
            # TODO: more escape?
            escape_char = "\\"
            return s\
                .replace(self.attr_separater, escape_char + self.attr_separater)\
                .replace(escape_char, escape_char + escape_char)\
                .replace(self.line_end, self.line_end_macro)

        buf = [ ]
        for r in receipients:
            attribute_values = [ r.attributes.get(k, "") for k in self.attribute_keys ]
            buf.append(self.field_separater.join([ r.open_id, "", "", self.attr_separater.join([escape(a) for a in attribute_values]) ]) + self.line_end)

        return "".join(buf)

    def create_template(self, template):
        # convert line end to lf
        # replace macro to mu style ###_ATTRIBUTE1_### (max 200)
        pattern = re.compile(self.macro_pattern)
        index = { }
        for idx, item in enumerate(self.attribute_keys):
            index[item] = 1 + idx

        def attr(m):
            if m and m.group(1) in index:
                return self.attribute_macro % index[m.group(1)]
            else:
                # keep original
                return m.group(0)

        return re.sub(pattern, attr, template)

    # TODO: tune parameters
    def pack_as_zip(self, start_time, template, receipients):
        buf = io.BytesIO()
        zip = zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False)
        structure = [
            [ "info.json", self.create_config(start_time) ],
            [ "TemplatePC_TXT.txt", self.create_template(template).encode('utf-8') ],
            [ "list.txt", self.create_list(receipients).encode('utf-8') ]
        ]
        for s in structure:
            (filename, content) = s
            zip.writestr(filename, content)
        zip.close()
        buf.seek(0)
        return buf.getvalue()
