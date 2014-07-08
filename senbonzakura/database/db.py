from senbonzakura.database.db_classes import Partial,Base,status_code
import senbonzakura.utils.oddity as oddity

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError # importing errors to make them availble too
from sqlalchemy.orm import sessionmaker
import logging

import pdb
import pprint

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


    def insert(self, identifier=None, status=None, start_timestamp=None, finish_timestamp=None):

        if not (identifier or status or start_timestamp or finish_timestamp):
            logging.warning('Could not insert record because all fields are blank')
            raise oddity.DBError('All fields of the record cannot be empty')

        temp_record = Partial(identifier=identifier, start_timestamp=start_timestamp, status=status, finish_timestamp=finish_timestamp)

        #pdb.set_trace()

        try:
            logging.info('Inserting record %s into db' % (temp_record,))
            self.session.add(temp_record)
            self.session.commit()

        except IntegrityError, e:
            print "Caught integrity error"
            logging.warning('Caught Integrity Error')
            self.session.rollback()
            # Integrity Error is thrown when 'Unique' constraint is violated.
            if self.lookup(identifier=identifier):
                logging.info('Record already exists')
                print 'Record already exists'
            else:
            # What is the error?
            # One of the specific ones will mean record already exists
            # if so handle appropriately
                logging.error('IntegrityError: %s' % e)
                raise oddity.DBError('Couldn\'t insert into DB, error: %s' % e)


    def reset_db(self):
        raise oddity.NotImplementedError()

    def query_db(self):
        raise oddity.NotImplementedError()


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
                # Do we really want to raise an error if a lookup fails?
                #raise oddity.DBError('Record with identifier %s does not exist' % identifier)
                return None
            return partial

    def update(self, identifier, status=None, finish_timestamp=None):
        # If none of the fields are given it's an error
        if all(x is None for x in (status, finish_timestamp)):
            raise oddity.DBError('No paramters detected for update.'
                                 'The params given are: %s' % locals())

        record = self.lookup(identifier=identifier)

        # Pretty code or ugly hack?
        #args = locals().copy()
        #for field in args.keys() if not args[field]:
        #    record.__dict__[field] = args[field]

        if finish_timestamp is not None:
            record.finish_timestamp = finish_timestamp

        if status is not None:
            record.status = status

        try:
            self.session.add(record)
            self.session.commit()
        except:
            logging.warning('Couldn\'t update record')
            raise
        finally: 
            logging.info('Record with identifier %s updated' % identifier)

    def close(self):
        self.session.close()

