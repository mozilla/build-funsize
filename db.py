from db_classes import Partial,Base,status_code
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError # importing errors to make them availble too
from sqlalchemy.orm import sessionmaker
import logging
import oddity

class Database(object):

    def __init__(self, db_uri):

        # Create new DB if doesn't exist
        logging.info('Initializing database %s' % db_uri)
        logging.debug('Creating db/db metadata')
        engine = create_engine(db_uri)
        Base.metadata.create_all(engine)

        # FIXME: Is one of these two lines redundant?
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        logging.info('DB session started')


    def insert(self, identifier=None, url=None, status=None, location=None):

        if not (identifier or url or status or location):
            logging.warning('Could not insert record because all fields are blank')
            raise oddity.DBError('All fields of the record cannot be empty')

        temp_record = Partial(identifier=identifier, url=url, status=status, location=location)

        try:
            logging.info('Inserting record %s into db' % (temp_record,))
            self.session.add(temp_record)
            self.session.commit()

        except IntegrityError, e:
            # What is the error?
            # One of the specific ones will mean record already exists
            # if so handle appropriately
            raise oddity.DBError('Couldn\'t insert into DB, error: %s' % e)


    def reset_db(self):
        pass

    def query_db(self):
        pass


    def lookup(self, identifier=None):
        #Why is the identifier optional?!
        """ Lookup by identifier. Return record if found, else None. """
        # FIXME: return a "copy" of the object and not the object from that
        # lookup itself because that causes the object to be modified for the
        # session

        try:
            partial = self.session.query(Partial).filter(Partial.identifier == identifier).first()

        except:
            # Probably needs to be handled much better than this.
            # What is the error raise when record doesn't exist
            logging.info('Lookup for record with identifier %s failed' % identifier)
            raise oddity.DBError('Lookup for identifier %s failed' % identifier)
        else:
            if partial is None:
                logging.debug('Record with identifier %s does not exist' % 
                              identifier)
                raise oddity.DBError('Record with identifier %s does not exist' % identifier)
            return partial

    def update(self, identifier, url=None, status=None, location=None):
        # If none of the fields are given it's an error
        if all(x is None for x in (url, status, location)):
            raise oddity.DBError('No paramters detected for update.'
                                 'The params given are: %s' % locals())

        record = self.lookup(identifier=identifier)

        # Pretty code or ugly hack?
        #args = locals().copy()
        #for field in args.keys() if not args[field]:
        #    record.__dict__[field] = args[field]

        if url is not None:
            record.url = url

        if location is not None:
            record.location = location

        if status is not None:
            record.status = status

        try:
            self.session.add(record)
            self.session.commit()
        except:
            logging.warning('Couldn\'t update log')
            raise
        finally: 
            logging.info('Record with identifier %s updated' % identifier)

    def close(self):
        self.session.close()

