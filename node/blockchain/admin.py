from django.contrib import admin

from .models import Account, Block, Node


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    pass


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    pass
