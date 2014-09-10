"""
senbonzakura.database.models
~~~~~~~~~~~~~~~~~~~~~

Defines the database schema and provides other convienent excpetions and
Enum-Style Dicts for status codes. Used directly only by db.py

"""

from sqlalchemy import Column, String, Integer, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

status_code = {'COMPLETED': 0,
               'ABORTED': 1,
               'IN_PROGRESS': 2,
               'INVALID': 3,
               }


class Partial(Base):
    """
    Defines the table called 'partial' in the database.
    Partial(int:id, str(65):identifier, int:status,
            char(1024):url, char(1024):location)

    :id:                Inbuilt ID, auto incremented.
                        Auto incremented. (is it?)

    :start_timestamp:   Time at which request was received in seconds
                        since epoch.

    :finish_timestamp:  Time at which request was completed in seconds
                        since epoch.

    :identifier:        The actual string (hash combination for now) used
                        to identify the partial mar.
                        The SQL 'UNIQUE' constraint is enforced on this column.
                        Can not be empty.
                        Defaults to -1.

    :status:            Integer field used to keep track of status, see
                        .status_code for mapping from integers to meaningful
                        statuses.  Can not be empty.  Defaults to -1.
    """
    __tablename__ = 'partial'

    status_code = {'COMPLETED': 0,
                   'ABORTED': 1,
                   'IN_PROGRESS': 2,
                   'INVALID': 3,
                   }


    id = Column(Integer, primary_key=True)
    start_timestamp = Column(BigInteger, default=-1, nullable=False)
    finish_timestamp = Column(BigInteger, default=-1)
    identifier = Column(String(500), nullable=False, unique=True)
    status = Column(Integer, nullable=False, default=-1)
