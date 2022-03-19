import logging
from collections import deque
from typing import Optional

from django.db.utils import Error
from djongo.base import DatabaseWrapper as DjongoDatabaseWrapper
from djongo.cursor import Cursor
from djongo.database import DatabaseError
from pymongo.client_session import ClientSession
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

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
        self.is_autocommit = False
        self.on_rollback_callables = deque()
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
        logger.debug('Rolling back...')
        if self.is_autocommit:
            self.on_rollback_callables.clear()
            return

        self._abort_transaction()
        self._end_session()

        on_rollback_callables = self.on_rollback_callables
        while on_rollback_callables:
            on_rollback_callables.popleft()()

    def _commit(self):
        logger.debug('Committing...')
        if self.is_autocommit:
            self.on_rollback_callables.clear()
            return

        if self.is_in_transaction():
            self.session.commit_transaction()
            logger.debug('Committed transaction for session: %s', id(self.session))
        else:
            logger.warning('Tried to commit outside transaction')

        self._end_session()
        self.on_rollback_callables.clear()

    def is_in_transaction(self):
        return (session := self.session) and session.in_transaction

    def _set_autocommit(self, autocommit):
        if autocommit:
            if self.is_in_transaction():
                logger.warning('Setting autocommit while in transaction')
                self._commit()
            elif self.session:
                self._end_session()

        self.is_autocommit = autocommit

    def create_cursor(self, name=None):
        logger.debug('Create cursor in wrapper: %s (session: %s)', id(self), id(self.session))
        if (session := self.session) is None and not self.is_autocommit:
            self.session = session = self.client_connection.start_session()

            # Starting transactions with non-default concerns to achieve READ COMMITTED isolation level as per
            # https://stackoverflow.com/questions/60156222/changing-mongodb-isolation-level-when-mongo-sessions-involved
            # https://jepsen.io/analyses/mongodb-4.2.6
            session.start_transaction(
                read_concern=ReadConcern(level='snapshot'), write_concern=WriteConcern('majority')
            )

            assert session.in_transaction
            logger.debug('Started transaction for session: %s', id(session))

        return CustomCursor(self.client_connection, self.connection, self.djongo_connection, session=session)

    def on_rollback(self, callable_):
        self.on_rollback_callables.append(callable_)
