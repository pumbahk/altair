from zope.interface import (
    Interface, 
    )

class IPromotionManager(Interface):
    def promotion_info(request, *args, **kwargs): #maybe
        pass

    def main_image_info(request):
        pass

    def show_image(image):
        pass
