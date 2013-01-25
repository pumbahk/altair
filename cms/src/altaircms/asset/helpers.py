# -*- coding:utf-8 -*-
import os
from datetime import date
import uuid
from .swfrect import swf_width_and_height


def get_writename(original_filename, gensym=uuid.uuid4, gendate=date.today):
    today = gendate().strftime('%Y-%m-%d')
    ext = original_filename[original_filename.rfind('.') + 1:]
    return '%s/%s.%s' % (today, gensym(), ext)

def write_buf(prefix, writename,  buf, _open=open):
    write_filepath = os.path.join(prefix, writename)

    dirpath = os.path.dirname(write_filepath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    with _open(write_filepath, "w+b") as dst_file:
        buf.seek(0)
        while 1:
            data = buf.read(26)
            if not data:
                break
            dst_file.write(data)
    size = buf.tell()
    buf.seek(0)
    return size

def _extract_tags(params, k):
    if k not in params:
        return []
    tags = [e.strip() for e in params.pop(k).split(",")] ##
    return [k for k in tags if k]

def divide_data(params):
    tags = _extract_tags(params, "tags")
    private_tags = _extract_tags(params, "private_tags")
    return tags, private_tags, params

def get_image_status_extra(form_parms, image_io):
    image_io.seek(0)
    width, height = Image.open(image_io).size
    return dict(width=width, height=height)

def get_movie_status_extra(form_parms, movie_io):
    return dict(width=None, height=None)

def get_flash_status_extra(form_parms, flash_io):
    flash_io.seek(0)
    width, height = swf_width_and_height(flash_io)
    return dict(width=width, height=height)

def get_asset_params_from_form_data(params):
    image_io = params["filepath"].file
    filename = params["filepath"].filename
    bufstring = image_io.read()

    mimetype = detect_mimetype(filename)
    _params = dict(params)
    _params.update({
        "mimetype": mimetype, 
        "buf": image_io, 
        "size": len(bufstring), 
        "filename": filename
        })
    return _params

def get_form_params_from_asset(asset):
    params = asset.to_dict()
    params["tags"] = tag.tags_to_string(asset.public_tags)
    params["private_tags"] = tag.tags_to_string(asset.private_tags)
    return params
