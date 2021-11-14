import pytest


@pytest.fixture
def account_root_file():
    return {
        '0067a4d2b153f62041a9cca5454aebd06ea1d0827828da889ddaad991d077401': {
            'balance': 47202,
            'balance_lock': '0067a4d2b153f62041a9cca5454aebd06ea1d0827828da889ddaad991d077401'
        },
        '009073c5985d3a715c3d44a33d5f928e893935fbab206d1d676d7d8b6e27ec85': {
            'balance': 281473944082589,
            'balance_lock': 'd0952a018fe694c76e49f679cb8bdd6470fc5a2e52fe80d03b8789f71aba03a6'
        }
    }
