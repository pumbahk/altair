import bpmappers as bp

class UnregisteredPageMapper(bp.Mapper):
    url = bp.RawField()
    title = bp.RawField()
    description = bp.RawField()
    keyword = bp.RawField()
    layout_id = bp.RawField()
    # tags = bp.RawField("tags") ## tag attribute is not supprted yet.

    @classmethod
    def as_mapper(cls, target):
        return cls(target).as_dict()
