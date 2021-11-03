def get_account_balance_cache_key(*, account_number):
    return f'account:{account_number}:balance'


def get_account_lock_cache_key(*, account_number):
    return f'account:{account_number}:lock'
