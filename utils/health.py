from django.http import JsonResponse
from django.db import connection
from django.conf import settings


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
        "version": "1.0.0",
    })