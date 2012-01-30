# -*- coding:utf-8 -*-

import sys
import os

"""
どんな画像が入っているか調べるのがめんどうになってつくった。 pngのみ

$ pwd
/home/podhmo/.virtualenvs/altair/docs/altair-doc/doc
$ python ./bin/images_diff.py

## resonse
== dir - doc ==
widget_icons.png
concrete_widget2.png
asset_detail.png
...snip

== doc - dir ==


"""

def image_file_in_doc(src):
    return os.popen('grep -r ".png" %s | sed "s/.*://g; s/.*images\///g;" | sort -u' % src).read().split("\n")

def image_file_in_dir(src):
    return [os.path.basename(f) for f in os.listdir(src) if f.endswith(".png")]

def diff(xs, ys):
    return sorted(set(xs).difference(set(ys)))



def main():
    if len(sys.argv) >= 2:
        src =  sys.argv[1]
    else:
        src = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../source")

    in_doc_images =  image_file_in_doc(src)
    in_dir_images = image_file_in_dir(os.path.join(src, "images"))

    print "== dir - doc =="
    print "\n".join(diff(in_dir_images, in_doc_images))
    print ""
    print "== doc - dir =="
    print "\n".join(diff(in_doc_images, in_dir_images))

if __name__ == "__main__":
    main()

