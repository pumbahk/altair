from altaircms.models import Base

def main(env):
    Base.metadata.drop_all()
    Base.metadata.create_all()
    
