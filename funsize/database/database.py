"""
funsize.database.database
~~~~~~~~~~~~~~~~~~~~~

This file contains the Database utilities, in essence wrapper functions that
make Insert, Update and Search operations on the database more convienent
to use.

"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from funsize.database.models import Partial, Base
import funsize.utils.oddity as oddity


class Database(object):
    """
    Database schema for the Partial metadata model

    """

    def __init__(self, db_uri):

        logging.info('Initializing database %s...', db_uri)
        engine = create_engine(db_uri)
        Base.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        logging.info('DB session started')

    def insert(self, identifier=None, status=None,
               start_timestamp=None, finish_timestamp=None):
        """ Method to map the insert operation into database
        """

        if not (identifier or status or start_timestamp or finish_timestamp):
            logging.warning('Could not insert because all fields are blank')
            raise oddity.DBError('All fields of the record cannot be empty')

        record = Partial(identifier=identifier,
                         start_timestamp=start_timestamp,
                         status=status,
                         finish_timestamp=finish_timestamp)

        try:
            logging.info('Inserting record %s into db', record)
            self.session.add(record)
            self.session.commit()
        except IntegrityError, e:
            logging.warning('Caught Integrity Error')
            self.session.rollback()
            if self.lookup(identifier=identifier):
                logging.info('Record already exists')
            else:
                logging.error('IntegrityError: %s', e)
                raise oddity.DBError('Could insert into DB, error: %s' % e)

    def reset_db(self):
        """ Method to dump and clean metadata database in case of need
        """

        raise oddity.FunsizeNotImplementedError()

    def lookup(self, identifier=None):
        """ Lookup by identifier. Return record if found, else None.
        """
        partial = self.session.query(Partial).filter(
            Partial.identifier == identifier).first()

        if partial is None:
            logging.debug('Record with identifier %s does not exist',
                          identifier)
        return partial

    def update(self, identifier, status=None, finish_timestamp=None):
        """
        Method to update a record in the database

        """

        if all(x is None for x in (status, finish_timestamp)):
            raise oddity.DBError('No paramters detected for update.'
                                 'The params given are: %s' % locals())

        record = self.lookup(identifier=identifier)
        if record is None:
            raise oddity.DBError('No partial with this identifier was found')

        if finish_timestamp is not None:
            record.finish_timestamp = finish_timestamp

        if status is not None:
            record.status = status

        try:
            self.session.add(record)
            self.session.commit()
        except:
            logging.warning('Could not update record')
            raise oddity.DBError('Could not update record')
        finally:
            logging.info('Record with identifier %s updated', identifier)

    def close(self):
        """
        Method to close the database binding connection
        """
        self.session.close()
