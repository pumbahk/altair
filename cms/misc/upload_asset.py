import sys
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse
import transaction
from pyramid.paster import bootstrap
from altaircms.auth.models import Organization
from altaircms.filelib.adapts import AfterCommit
from altaircms.filelib.s3 import S3Event
from altaircms.filelib.core import DummyFile
from altaircms.asset.api import get_asset_model_abspath, get_asset_model_abspath_thumbnail
from altaircms.asset.creation import get_asset_filesession
from altaircms.asset.subscribers import publish_files_on_s3
from altaircms.asset.subscribers import unpublish_files_on_s3
import os.path

def main():
    parser = argparse.ArgumentParser(description="register category top page", formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("config", help=u"development.ini'")
    parser.add_argument("type", help=u"asset type", choices=["image", "movie", "flash"])
    parser.add_argument("action", choices=["upload", "publish", "unpublish", "delete"])
    parser.add_argument("organization_shortname",  help=u"organization_shortname")
    parser.add_argument('infile', help=u"file", nargs='?', type=argparse.FileType('r'), 
                        default=sys.stdin)
    args = parser.parse_args()
    _main(args)

def get_assets_collect_function(args_type):
    if args_type == "image":
        return image_collect
    elif args_type == "movie":
        return movie_collect
    elif args_type == "flash":
        return flash_collect

def _main(args):
    try:
        env = bootstrap(args.config)
        run(env, args)
        transaction.commit()
    except Exception, e:
        transaction.abort()
        logger.exception(str(e))

def run(env, args):
    from altaircms.models import DBSession
    organization = Organization.query.filter_by(short_name=args.organization_shortname).one()
    ids = get_ids(args.infile)
    assets = get_assets_collect_function(args.type)(organization, ids)
    request = env["request"]
    request.organization = organization
    if args.action == "upload":
        event = AfterCommit(request=request, 
                            session=get_asset_filesession(request), 
                            result={"create": list(files_from_assets(request, assets)), 
                                    "extra_args": assets}, 
                            options={"public": True},                        
                            )
        request.registry.notify(event)
        DBSession.add_all(assets)
    elif args.action == "publish":
        from altaircms.filelib.interfaces import IS3UtilityFactory
        uploader = request.registry.queryUtility(IS3UtilityFactory).uploader
        event = S3Event(request=request, 
                        session=get_asset_filesession(request), 
                        files=list(files_from_assets(request, assets)), 
                        uploader=uploader, 
                        extra_args=assets, 
                        )
        publish_files_on_s3(event)
    elif args.action == "unpublish":
        from altaircms.filelib.interfaces import IS3UtilityFactory
        uploader = request.registry.queryUtility(IS3UtilityFactory).uploader
        event = S3Event(request=request, 
                        session=get_asset_filesession(request), 
                        files=list(files_from_assets(request, assets)), 
                        uploader=uploader, 
                        extra_args=assets, 
                        )
        unpublish_files_on_s3(event)
    elif args.action == "delete":
        event = AfterCommit(request=request, 
                            session=get_asset_filesession(request), 
                            result={"delete": list(files_from_assets(request, assets)), 
                                    "extra_args": assets}, 
                            options={"public": True},                        
                            )
        request.registry.notify(event)
        DBSession.delet_all(assets)



        
def get_ids(io):
    return [x.strip() for x in iter(io.readline, "")]

def get_exist_filepath(realpath):
    if not os.path.exists(realpath):
        logger.warn("{0} is not found".format(realpath))
        return None
    return realpath

def files_from_assets(request, assets):
    for a in assets:
        realpath = get_exist_filepath(get_asset_model_abspath(request, a))
        if realpath:
            yield (DummyFile(name=a.filepath), realpath)
        thumbnail_path = get_asset_model_abspath_thumbnail(request, a)
        if thumbnail_path:
            thumbnail_path = get_exist_filepath(thumbnail_path)
            if thumbnail_path:
                yield (DummyFile(name=a.thumbnail_path), thumbnail_path)

def image_collect(organization, ids):
    from altaircms.asset.models import ImageAsset
    return ImageAsset.query.filter(ImageAsset.id.in_(ids), ImageAsset.organization_id==organization.id).all()

def movie_collect(organization, ids):
    from altaircms.asset.models import MovieAsset
    return MovieAsset.query.filter(MovieAsset.id.in_(ids), MovieAsset.organization_id==organization.id).all()

def flash_collect(organization, ids):
    from altaircms.asset.models import FlashAsset
    return FlashAsset.query.filter(FlashAsset.id.in_(ids), FlashAsset.organization_id==organization.id).all()

if __name__ == "__main__":
    main()
