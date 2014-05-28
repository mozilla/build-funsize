from db_classes import Partial,Base,status_code
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError # importing errors to make them availble too
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///test.db')

# Is one of these two lines redundant?
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

def insert(identifier=None, url=None, status=None, location=None):

    temp_record = Partial(identifier=identifier, url=url, status=status, location=location)
    try:
        session.add(temp_record)
        session.commit()
    except IntegrityError, e:
        # What is the error?
        # One of the specific ones will mean record already exists
        # if so handle appropriately
        print "Couldn't insert into DB, error: %s" % e
        raise


def reset_db():
    pass

def query_db():
    pass

#def retrieve():
#    pass

def lookup(identifier=None):
    """ Return record if found, else None """

    try:
        partial = session.query(Partial).filter(Partial.identifier == identifier).first()
        return partial
    except:
        # Probably needs to be handled much better than this.
        # What is the error raise when record doesn't exist
        print "Couldn't lookup, exception"
        #raise
        return None

def update(identifier, url=None, status=None, location=None):
    # If none of the fields are given it's an error
    if not (url or status or location):
        # raise error, or fail or something
        print "Wrong params"
        print "given params are:"
        print locals()
    record = lookup(identifier=identifier)

    # Pretty code or ugly hack?
    #args = locals().copy()
    #for field in args.keys() if not args[field]:
    #    record.__dict__[field] = args[field]

    if url:
        record.url = url

    if location:
        record.location = location

    if status:
        record.status = status

    session.add(record)
    session.commit()

