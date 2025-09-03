
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils.encoding import smart_str
from django.db.models import Q

from .models import DocumentModel, UserModel, AuditLog
from .services import DatabaseConnector, EncryptionManager, DocumentManager

# ----- Minimal APIs (as before) -----
def hello_view(request):
    return JsonResponse({"msg": "Hello from Python-only docsign (plus)"})

@csrf_exempt
def upload_pdf(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    title = request.POST.get("title", "Untitled")
    pdf = request.FILES.get("file")
    if not pdf:
        return JsonResponse({"error": "no file"}, status=400)
    db = DatabaseConnector(); enc = EncryptionManager(); mgr = DocumentManager(db, enc)
    doc = mgr.upload_pdf(user_name="Zahra", user_role="lawyer", title=title, file_name=pdf.name, file_bytes=pdf.read())
    return JsonResponse({"ok": True, "doc_id": doc.id, "version": doc.version})

@csrf_exempt
def sign_doc(request, doc_id: int):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    db = DatabaseConnector(); enc = EncryptionManager(); mgr = DocumentManager(db, enc)
    sig = mgr.sign_document(doc_id, signer_name="Zahra", signer_role="lawyer")
    return JsonResponse({"ok": True, "doc_id": doc_id, "signature_len": len(sig.signature_bytes)})

def verify_doc(request, doc_id: int):
    db = DatabaseConnector(); enc = EncryptionManager(); mgr = DocumentManager(db, enc)
    ok = mgr.verify_document(doc_id)
    return JsonResponse({"verified": ok})

# ----- Optional UI (no JS build; just HTML) -----
def index(request):
    return render(request, "core/index.html", {})

def doc_list(request):
    q = request.GET.get("q", "").strip()
    docs = DocumentModel.objects.all().order_by("-created_at", "-version")
    if q:
        docs = docs.filter(Q(title__icontains=q))
    paginator = Paginator(docs, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "core/doc_list.html", {"page_obj": page_obj, "q": q})

def doc_detail(request, doc_id: int):
    doc = get_object_or_404(DocumentModel, id=doc_id)
    return render(request, "core/doc_detail.html", {"doc": doc})

def doc_download(request, doc_id: int):
    doc = get_object_or_404(DocumentModel, id=doc_id)
    if not doc.pdf_file:
        raise Http404("No file")
    AuditLog.objects.create(actor=None, action="DOWNLOAD", target_doc=doc, meta={"filename": doc.pdf_file.name})
    return FileResponse(open(doc.pdf_file.path, "rb"), as_attachment=True, filename=smart_str(doc.pdf_file.name.split("/")[-1]))

def doc_delete(request, doc_id: int):
    doc = get_object_or_404(DocumentModel, id=doc_id)
    title = doc.title
    doc.delete()
    AuditLog.objects.create(actor=None, action="DELETE", target_doc=None, meta={"title": title})
    return redirect("doc_list")

# ----- Utilities -----
def audit_csv(request):
    rows = AuditLog.objects.order_by("-timestamp").all()
    lines = ["timestamp,action,doc_id,actor_id,meta"]
    for r in rows:
        lines.append(f"{r.timestamp},{r.action},{r.target_doc_id},{r.actor_id},{r.meta}")
    data = "\n".join(lines)
    resp = HttpResponse(data, content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="audit.csv"'
    return resp

@csrf_exempt
def ensure_keys(request):
    db = DatabaseConnector()
    user = db.get_or_create_user("Zahra", "lawyer")
    pub, priv = db.ensure_user_keys(user)
    return JsonResponse({"ok": True, "public_key_len": len(pub), "private_key_len": len(priv)})  # DEMO ONLY
