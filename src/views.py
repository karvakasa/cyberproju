from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.hashers import check_password
from .models import Credential, Note

def home(request):
    flaws = [
        {
            "category": "A01",
            "name": "Broken Access Control",
            "url": "src:insecure-note-detail",
            "description": "A note can be read by changing only its numeric ID in url.",
        },
        {
            "category": "A02",
            "name": "Cryptographic Failures",
            "url": "src:insecure-credentials",
            "description": "Credentials are exposed, and weak password hashing is used.",
        },
        {
            "category": "A03",
            "name": "Injection",
            "url": "src:insecure-search",
            "description": "Normal search shows only the current user's notes; SQL injection can bypass the owner filter. Like ' OR 1=1 --",
        },
        {
            "category": "A05",
            "name": "Security Misconfiguration",
            "url": "src:home",
            "description": "Debug mode and a hard coded secret key are in settings.py, not in .env",
        },
        {
            "category": "A07",
            "name": "Identification and Authentication Failures",
            "url": "src:insecure-login",
            "description": "login link with correct username and any password.",
        },
    ]
    return render(request, "home.html", {"flaws": flaws})


def insecure_note_detail(request, note_id):
    # A01: return any note without checking the current user's ownership.

    note = get_object_or_404(Note, pk=note_id)
    
    # A01 note never checks the current user against note owner.
    # Fix checks current user against note owner

    """ current_user = request.session.get("user")
    note = get_object_or_404(Note, pk=note_id, owner=current_user) """

    return render(request, "home.html", {"note": note})


def insecure_credentials(request):
    # A02: expose weak password digests to an unauthenticated caller.
    credentials = list(
        Credential.objects.values("username", "password")
    )

    # Fix requires the session and never return password data.
    # Demands that you log in to see your own username.
    
    """ current_user = request.session.get("user")
    if not current_user:
        return JsonResponse({"error": "Authentication required"}, status=401)
    return JsonResponse({"username": current_user}) """

    return JsonResponse({"credentials": credentials})


def insecure_search(request):
    term = request.GET.get("q", "")
    current_user = request.session.get("user", "")
    table = Note._meta.db_table
    # A03
    # A normal search with "note" will return only the current user's notes.
    # "' OR 1=1 --" bypasses that owner condition and returns every note.
    
    sql = (
        "SELECT id, title, body, owner FROM %s "
        "WHERE owner = '%s' AND title LIKE '%%%s%%' "
        "OR owner = '%s' AND body LIKE '%%%s%%'"
    ) % (table, current_user, term, current_user, term)

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as exc:  # noqa: BLE001 - intentionally visible baseline
        return JsonResponse({"error": str(exc), "query": sql}, status=400)

    # Fixed version: require a logged-in user to find anything
    # values are put to parameters instead directly into SQL.

    """ current_user = request.session.get("user")
    if not current_user:
        return JsonResponse({"error": "Authentication required"}, status=401)
    pattern = "%%%s%%" % term
    safe_sql = (
       "SELECT id, title, body, owner FROM %s "
       "WHERE owner = %%s AND (title LIKE %%s OR body LIKE %%s)"
    ) % connection.ops.quote_name(Note._meta.db_table)
    with connection.cursor() as cursor:
       cursor.execute(safe_sql, [current_user, pattern, pattern])
       columns = [column[0] for column in cursor.description]
       results = [dict(zip(columns, row)) for row in cursor.fetchall()] """

    if not term.strip():
        return JsonResponse({"results": []})
    return JsonResponse({"results": results})


def insecure_login(request):
    # A07: create a session for any known username without a password.
    username = request.GET.get("username", "")
    supplied_password = request.GET.get("password", "")
    credential_exists = Credential.objects.filter(username=username).exists()

    # A07 vulnerable baseline: `supplied_password` is deliberately ignored.
    if not credential_exists:
        return JsonResponse({"authenticated": False}, status=401)
    request.session["user"] = username
    return JsonResponse(
        {
            "authenticated": True,
            "username": username,
            "password_was_checked": bool(supplied_password) and False,
        }
    )

    # Fixed version: validate the supplied password with Django's password hasher
    # Fix version checks the password and returns error if not correct
    # 

    """ credential = Credential.objects.filter(username=username).first()
    if credential is None or not check_password(supplied_password, credential.password):
        return JsonResponse({"authenticated": False}, status=401)
    request.session.cycle_key()
    request.session["user"] = username
    return JsonResponse({"authenticated": True, "username": username}) """
