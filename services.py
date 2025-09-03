
from dataclasses import dataclass
from typing import Optional
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .models import UserModel, DocumentModel, SignatureModel, AuditLog
from . import crypto

@dataclass
class User:
    id: int
    name: str
    role: str

class EncryptionManager:
    def generate_keys(self):
        return crypto.generate_keys()

    def sign(self, private_key_pem: bytes, data: bytes) -> bytes:
        return crypto.sign_bytes(private_key_pem, data)

    def verify(self, public_key_pem: bytes, data: bytes, signature: bytes) -> bool:
        return crypto.verify_signature(public_key_pem, data, signature)

class DatabaseConnector:
    def get_or_create_user(self, name: str, role: str) -> UserModel:
        user, _ = UserModel.objects.get_or_create(name=name, defaults={'role': role})
        if user.role != role:
            user.role = role
            user.save(update_fields=['role'])
        return user

    def ensure_user_keys(self, user: UserModel):
        if not user.public_key_pem or not user.private_key_pem:
            pub, priv = crypto.generate_keys()
            user.public_key_pem = pub
            user.private_key_pem = priv  # DEMO ONLY
            user.save(update_fields=['public_key_pem', 'private_key_pem'])
        return user.public_key_pem, user.private_key_pem

    def create_document(self, title: str, created_by: UserModel, file_name: str, file_bytes: bytes, version: int = 1) -> DocumentModel:
        content = ContentFile(file_bytes, name=file_name)
        doc = DocumentModel.objects.create(title=title, version=version, created_by=created_by, pdf_file=content)
        return doc

    def get_latest_version(self, title: str) -> Optional[DocumentModel]:
        return DocumentModel.objects.filter(title=title).order_by('-version').first()

    def get_document(self, doc_id: int) -> DocumentModel:
        return DocumentModel.objects.get(id=doc_id)

    def add_signature(self, doc: DocumentModel, signer: UserModel, signature_bytes: bytes, public_key_pem: bytes) -> SignatureModel:
        return SignatureModel.objects.create(document=doc, signer=signer, signature_bytes=signature_bytes, public_key_pem=public_key_pem)

    def log(self, actor: Optional[UserModel], action: str, doc: Optional[DocumentModel], meta: dict = None):
        AuditLog.objects.create(actor=actor, action=action, target_doc=doc, meta=meta or {})

class DocumentManager:
    def __init__(self, db: DatabaseConnector, enc: EncryptionManager):
        self.db = db
        self.enc = enc

    def upload_pdf(self, user_name: str, user_role: str, title: str, file_name: str, file_bytes: bytes) -> DocumentModel:
        user = self.db.get_or_create_user(user_name, user_role)
        last = self.db.get_latest_version(title)
        version = 1 if not last else last.version + 1
        doc = self.db.create_document(title, user, file_name, file_bytes, version)
        self.db.log(user, 'UPLOAD', doc, {'filename': file_name, 'version': version})
        return doc

    def sign_document(self, doc_id: int, signer_name: str, signer_role: str):
        user = self.db.get_or_create_user(signer_name, signer_role)
        pub_pem, priv_pem = self.db.ensure_user_keys(user)
        doc = self.db.get_document(doc_id)
        data = default_storage.open(doc.pdf_file.name, 'rb').read()
        signature = self.enc.sign(priv_pem, data)
        sig = self.db.add_signature(doc, user, signature, pub_pem)
        self.db.log(user, 'SIGN', doc, {'signature_len': len(signature)})
        return sig

    def verify_document(self, doc_id: int) -> bool:
        doc = self.db.get_document(doc_id)
        sig = doc.signatures.order_by('-id').first()
        if not sig:
            self.db.log(None, 'VERIFY', doc, {'ok': False, 'reason': 'no signature'})
            return False
        data = default_storage.open(doc.pdf_file.name, 'rb').read()
        ok = self.enc.verify(sig.public_key_pem, data, sig.signature_bytes)
        self.db.log(None, 'VERIFY', doc, {'ok': ok})
        return ok
