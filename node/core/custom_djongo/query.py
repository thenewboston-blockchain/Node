import logging

from djongo.sql2mongo.query import DeleteQuery, InsertQuery, Query, SelectQuery, UpdateQuery
from pymongo import ReturnDocument

from . import InitSessionMixin

logger = logging.getLogger(__name__)


class CustomUpdateQuery(InitSessionMixin, UpdateQuery):

    def execute(self):
        self.result = self.db[self.left_table].update_many(**self.kwargs, session=self.session)
        logger.debug(f'update_many: {self.result.modified_count}, matched: {self.result.matched_count}')


class CustomDeleteQuery(InitSessionMixin, DeleteQuery):

    def execute(self):
        self.result = self.db[self.left_table].delete_many(**self.kw, session=self.session)
        logger.debug('delete_many: {}'.format(self.result.deleted_count))


class CustomInsertQuery(InitSessionMixin, InsertQuery):

    def execute(self):
        docs = []
        num = len(self._values)

        filter_ = {'name': self.left_table, 'auto': {'$exists': True}}
        update = {'$inc': {'auto.seq': num}}
        auto = self.db['__schema__'].find_one_and_update(filter_, update, return_document=ReturnDocument.AFTER)

        for i, val in enumerate(self._values):
            ins = {}
            if auto:
                for name in auto['auto']['field_names']:
                    ins[name] = auto['auto']['seq'] - num + i + 1
            for _field, value in zip(self._cols, val):
                if auto and _field in auto['auto']['field_names'] and value == 'DEFAULT':
                    continue
                ins[_field] = value
            docs.append(ins)

        res = self.db[self.left_table].insert_many(docs, ordered=False, session=self.session)
        if auto:
            self._result_ref.last_row_id = auto['auto']['seq']
        else:
            self._result_ref.last_row_id = res.inserted_ids[-1]
        logger.debug('inserted ids {}'.format(res.inserted_ids))


class CustomSelectQuery(InitSessionMixin, SelectQuery):

    def _get_cursor(self):
        if self._needs_aggregation():
            pipeline = self._make_pipeline()
            cur = self.db[self.left_table].aggregate(pipeline, session=self.session)
            logger.debug(f'Aggregation query: {pipeline}')
        else:
            kwargs = {}
            if self.where:
                kwargs.update(self.where.to_mongo())

            if self.selected_columns:
                kwargs.update(self.selected_columns.to_mongo())

            if self.limit:
                kwargs.update(self.limit.to_mongo())

            if self.order:
                kwargs.update(self.order.to_mongo())

            if self.offset:
                kwargs.update(self.offset.to_mongo())

            cur = self.db[self.left_table].find(**kwargs, session=self.session)
            logger.debug(f'Find query: {kwargs}')

        return cur


class CustomQuery(InitSessionMixin, Query):

    def _update(self, sm):
        query = CustomUpdateQuery(self.db, self.connection_properties, sm, self._params, session=self.session)
        query.execute()
        return query

    def _delete(self, sm):
        query = CustomDeleteQuery(self.db, self.connection_properties, sm, self._params, session=self.session)
        query.execute()
        return query

    def _insert(self, sm):
        query = CustomInsertQuery(self, self.db, self.connection_properties, sm, self._params, session=self.session)
        query.execute()
        return query

    def _select(self, sm):
        return CustomSelectQuery(self.db, self.connection_properties, sm, self._params, session=self.session)


CustomQuery.FUNC_MAP.update({
    'SELECT': CustomQuery._select,
    'UPDATE': CustomQuery._update,
    'INSERT': CustomQuery._insert,
    'DELETE': CustomQuery._delete,
})
