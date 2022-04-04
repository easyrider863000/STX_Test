from django.http import JsonResponse
from . import models
from . import serialezers
from django.db.models import Max, Min
from .check_errors import CheckErrors


def search(request):
    start_date = ""
    finish_date = ""
    langname = ""
    inauthor = ""
    intitle = ""

    if request.GET.get("searchfromdate", "found") != "found":
        start_date = request.GET["searchfromdate"]
    if request.GET.get("searchuptodate", "found") != "found":
        finish_date = request.GET["searchuptodate"]
    if request.GET.get("searchlanguage", "found") != "found":
        langname = request.GET["searchlanguage"]
    if request.GET.get("searchinauthor", "found") != "found":
        inauthor = request.GET["searchinauthor"]
    if request.GET.get("searchintitle", "found") != "found":
        intitle = request.GET["searchintitle"]

    if not CheckErrors.checkSearchString(start_date):
        start_date = models.Book.objects.all(
            ).aggregate(Min('publishdate'))["publishdate__min"]
    if not CheckErrors.checkSearchString(finish_date):
        finish_date = models.Book.objects.all(
        ).aggregate(Max('publishdate'))["publishdate__max"]

    langs = models.Language.objects.filter(langname__contains=langname)
    author_filters = models.Author.objects.filter(
        authorname__contains=inauthor)
    authors = models.Bookauthor.objects.filter(authorid__in=author_filters)
    books = models.Book.objects.filter(
        id__in=[item.bookid.id for item in authors],
        langid__in=langs,
        publishdate__lte=finish_date,
        publishdate__gte=start_date,
        title__contains=intitle)
    isbns = models.Isbnnumber.objects.all()
    books_output = []
    for item in books:
        books_output.append(serialezers.BookSerialiser.serialize(
            item,
            [author.authorid for author in authors
                if author.bookid.id == item.id],
            [isbn for isbn in isbns if isbn.bookid.id == item.id]
        ))
    return JsonResponse({"books": books_output})
