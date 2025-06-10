from .models import MissingVideoReport

def missing_videos_count(request):
    if request.user.is_staff:
        pendientes = MissingVideoReport.objects.filter(resolved=False).count()
    else:
        pendientes = 0
    return {'missing_video_reports_count': pendientes}