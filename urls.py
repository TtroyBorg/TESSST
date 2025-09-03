
from django.urls import path
from .views import (
    index, doc_list, doc_detail, doc_download, doc_delete,
    hello_view, upload_pdf, sign_doc, verify_doc, audit_csv, ensure_keys
)

urlpatterns = [
    path('', index, name='index'),
    path('docs/', doc_list, name='doc_list'),
    path('docs/<int:doc_id>/', doc_detail, name='doc_detail'),
    path('docs/<int:doc_id>/download/', doc_download, name='doc_download'),
    path('docs/<int:doc_id>/delete/', doc_delete, name='doc_delete'),
    path('audit.csv', audit_csv, name='audit_csv'),

    # APIs
    path('hello/', hello_view),
    path('api/upload/', upload_pdf),
    path('api/sign/<int:doc_id>/', sign_doc),
    path('api/verify/<int:doc_id>/', verify_doc),
    path('api/keys/ensure/', ensure_keys, name='ensure_keys'),
]
