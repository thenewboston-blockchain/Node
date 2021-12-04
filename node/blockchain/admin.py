from django.contrib import admin

from .models import AccountState, Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    pass


@admin.register(AccountState)
class AccountStateAdmin(admin.ModelAdmin):
    pass
