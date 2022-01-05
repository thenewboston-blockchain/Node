from djongo.features import DatabaseFeatures as BaseDatabaseFeatures


class DatabaseFeatures(BaseDatabaseFeatures):
    supports_transactions = True
