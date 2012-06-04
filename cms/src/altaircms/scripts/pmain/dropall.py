from altaircms.models import Base

def main(env, args):
    Base.metadata.drop_all()
    Base.metadata.create_all()
    
