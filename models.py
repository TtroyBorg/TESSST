
from django.db import models

class UserModel(models.Model):
    name = models.CharField(max_length=200, unique=True)
    role = models.CharField(max_length=50)

    # DEMO ONLY: store keys in DB (not recommended for production)
    public_key_pem = models.BinaryField(null=True, blank=True)
    private_key_pem = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

class DocumentModel(models.Model):
    title = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    created_by = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to="docs/")

    def __str__(self):
        return f"{self.title} v{self.version}"

class SignatureModel(models.Model):
    document = models.ForeignKey(DocumentModel, related_name="signatures", on_delete=models.CASCADE)
    signer = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    signed_at = models.DateTimeField(auto_now_add=True)
    signature_bytes = models.BinaryField()
    public_key_pem = models.BinaryField()

    def __str__(self):
        return f"Signature(doc={self.document_id}, signer={self.signer_id})"

class AuditLog(models.Model):
    actor = models.ForeignKey(UserModel, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)  # UPLOAD/SIGN/VERIFY/DOWNLOAD/DELETE
    target_doc = models.ForeignKey(DocumentModel, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.timestamp} {self.action} doc={self.target_doc_id} actor={self.actor_id}"
