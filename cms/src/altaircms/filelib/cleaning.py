import os
import shutil

"""
Event(request, root)  
"""
_EXCLUDES = [".DS_Store"]
def delete_needless_files(event, excludes=_EXCLUDES):
    root = event.root
    for root, dirs, files in os.walk(root):
        for d in  dirs:
            if d in excludes:
                shutil.rmtree(os.path.join(root, d))
