
from django.contrib import admin
from .models import UserModel, DocumentModel, SignatureModel, AuditLog

@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "role")

@admin.register(DocumentModel)
class DocAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "version", "created_by", "created_at")

@admin.register(SignatureModel)
class SigAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "signer", "signed_at")

@admin.register(AuditLog)
class LogAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "target_doc", "actor", "timestamp")
