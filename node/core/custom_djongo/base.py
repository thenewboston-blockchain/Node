import logging
from typing import Optional

from django.db.utils import Error
from djongo.base import DatabaseWrapper as DjongoDatabaseWrapper
from djongo.cursor import Cursor
from djongo.database import DatabaseError
from pymongo.client_session import ClientSession

from node.core.custom_djongo.query import CustomQuery

from . import InitSessionMixin
from .features import DatabaseFeatures

logger = logging.getLogger(__name__)


# TODO(dmu) MEDIUM: Implement a better support for MongoDB transactions
class CustomCursor(InitSessionMixin, Cursor):

    def execute(self, sql, params=None):
        try:
            self.result = CustomQuery(
                self.client_conn, self.db_conn, self.connection_properties, sql, params, session=self.session
            )
        except Exception as e:
            db_exe = DatabaseError()
            raise db_exe from e


class DatabaseWrapper(DjongoDatabaseWrapper):
    features_class = DatabaseFeatures

    def __init__(self, *args, **kwargs):
        self.session: Optional[ClientSession] = None
        super().__init__(*args, **kwargs)

    def _abort_transaction(self):
        if (session := self.session) and session.in_transaction:
            session.abort_transaction()
            logger.debug('Aborted (rolled back) transaction for session: %s', id(session))
        else:
            raise Error('Rolling back outside transaction')

    def _end_session(self):
        if session := self.session:
            assert not session.has_ended
            session.end_session()
            self.session = None
            logger.debug('Ended session: %s', id(session))

    def _close(self):
        """
        Closes the client connection to the database.
        """
        if session := self.session:
            if session.in_transaction:
                logger.warning('Aborting transaction implicitly')
                self._abort_transaction()

            self._end_session()

        super()._close()

    def _rollback(self):
        self._abort_transaction()
        self._end_session()

    def _commit(self):
        if (session := self.session) and session.in_transaction:
            session.commit_transaction()
            logger.debug('Committed transaction for session: %s', id(session))
        else:
            logger.warning('Tried to commit outside transaction')

        self._end_session()

    def create_cursor(self, name=None):
        logger.debug('Create cursor in wrapper: %s (session: %s)', id(self), id(self.session))
        if (session := self.session) is None:
            self.session = session = self.client_connection.start_session()
            session.start_transaction()
            assert session.in_transaction
            logger.debug('Started transaction for session: %s', id(session))

        return CustomCursor(self.client_connection, self.connection, self.djongo_connection, session=session)
