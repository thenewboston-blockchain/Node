from django.contrib import admin

from .models import AccountState, Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    # TODO(dmu) MEDIUM: Improve representation of `body` field so it fits/wraps in the form nicely
    fields = ('_id', 'body')
    readonly_fields = fields


@admin.register(AccountState)
class AccountStateAdmin(admin.ModelAdmin):
    list_display = ('_id',)
