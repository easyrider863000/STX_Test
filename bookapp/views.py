from django.shortcuts import render, redirect
from . import models
from django.db.models import Max, Min
from requests import get
from .check_errors import CheckErrors
from datetime import date


def index(request):
    books = models.Book.objects.all()
    authors = models.Bookauthor.objects.all()
    isbns = models.Isbnnumber.objects.all()

    books_output = []
    for item in books:
        books_output.append({"book": item,
                             "authors": [author.authorid for author in authors
                                         if author.bookid.id == item.id],
                             "isbns": [isbn for isbn in isbns
                                       if isbn.bookid.id == item.id]})
    return render(request, "bookList.html", context={"books": books_output})


def importBook(request):
    q = request.GET.get('q')
    if not CheckErrors.checkSearchString(q):
        return render(request, "importBookList.html",
                      context={"errors": "Search string is invalid."})
    params_string = ""
    if CheckErrors.checkSearchString(request.GET.get('searchintitle')):
        params_string += "+intitle:" + str(request.GET.get('searchintitle'))
    if CheckErrors.checkSearchString(request.GET.get('searchinauthor')):
        params_string += "+inauthor:" + str(request.GET.get('searchinauthor'))
    if CheckErrors.checkSearchString(request.GET.get('searchinpublisher')):
        params_string += "+inpublisher:" + str(request.GET.get('searchinpublisher'))
    if CheckErrors.checkSearchString(request.GET.get('searchsubject')):
        params_string += "+subject:" + str(request.GET.get('searchsubject'))
    if CheckErrors.checkSearchString(request.GET.get('searchisbn')):
        params_string += "+isbn:" + str(request.GET.get('searchisbn'))
    if CheckErrors.checkSearchString(request.GET.get('searchlccn')):
        params_string += "+lccn:" + str(request.GET.get('searchlccn'))
    if CheckErrors.checkSearchString(request.GET.get('searchoclc')):
        params_string += "+oclc:" + str(request.GET.get('searchoclc'))
    result = get("https://www.googleapis.com/books/v1/volumes?q=" + q + params_string)
    return render(request, "importBookList.html", context={"books": result.json()})


def addBooksFromImport(request):
    for link in request.POST.getlist("book"):
        book = get(link).json()

        book_language = ""
        book_publisheddate = ""
        book_authors = []
        book_isbns = []
        book_pagecount = 2
        book_title = ""
        book_picture = ""

        if book["volumeInfo"].get("language", "found") != "found":
            book_language = book["volumeInfo"]["language"]
        if book["volumeInfo"].get("publishedDate", "found") != "found":
            book_publisheddate = book["volumeInfo"]["publishedDate"]
        if book["volumeInfo"].get("authors", "found") != "found":
            book_authors = book["volumeInfo"]["authors"]
        if book["volumeInfo"].get("industryIdentifiers", "found") != "found":
            book_isbns = book["volumeInfo"]["industryIdentifiers"]
        if book["volumeInfo"].get("pageCount", "found") != "found":
            book_pagecount = int(book["volumeInfo"]["pageCount"])
        if book["volumeInfo"].get("title", "found") != "found":
            book_title = book["volumeInfo"]["title"]
        if book["volumeInfo"].get("imageLinks", "found") != "found" \
                and book["volumeInfo"]["imageLinks"].get("thumbnail", "found") != "found":
            book_picture = book["volumeInfo"]["imageLinks"]["thumbnail"]

        langid, created = models.Language.objects.get_or_create(langname=book_language)

        input_date = book_publisheddate.split("-")
        publish_date = date(
            (int(input_date[0]) if len(input_date) > 1 else 2000),
            (int(input_date[1]) if len(input_date) > 1 else 1),
            (int(input_date[2]) if len(input_date) > 2 else 1))
        bookid, created = models.Book.objects.get_or_create(
            title=book_title,
            langid=langid,
            countpages=book_pagecount,
            publishdate=publish_date,
            defaults={'picture': book_picture})

        for author in book_authors:
            authorid, created = models.Author.objects.get_or_create(authorname=author)
            bookauthorid, created = models.Bookauthor.objects.get_or_create(authorid=authorid, bookid=bookid)

        for isbn in book_isbns:
            isbn, created = models.Isbnnumber.objects.get_or_create(isbn=isbn["identifier"], bookid=bookid)
    return redirect("/")


def searchBook(request):
    start_date = request.GET.get('searchfromdate')
    finish_date = request.GET.get('searchuptodate')
    if not CheckErrors.checkSearchString(start_date):
        start_date = models.Book.objects.all().aggregate(Min('publishdate'))["publishdate__min"]
    if not CheckErrors.checkSearchString(finish_date):
        finish_date = models.Book.objects.all().aggregate(Max('publishdate'))["publishdate__max"]

    langs = models.Language.objects.filter(langname__contains=str(request.GET.get('searchlanguage')))
    author_filters = models.Author.objects.filter(authorname__contains=str(request.GET.get('searchinauthor')))
    authors = models.Bookauthor.objects.filter(authorid__in=author_filters)
    books = models.Book.objects.filter(id__in=[item.bookid.id for item in authors],
                                       langid__in=langs,
                                       publishdate__lte=finish_date,
                                       publishdate__gte=start_date,
                                       title__contains=str(request.GET.get('searchintitle')))
    isbns = models.Isbnnumber.objects.all()

    books_output = []
    for item in books:
        books_output.append({"book": item,
                             "authors": [author.authorid for author in authors if author.bookid.id == item.id],
                             "isbns": [isbn for isbn in isbns if isbn.bookid.id == item.id]})

    return render(request, "bookList.html", context={"books": books_output})


def addNewBook(request):
    book_title = str(request.POST.get("title"))
    book_publisheddate = str(request.POST.get("publishdate"))
    book_authors = ([item.rstrip().lstrip() for item in request.POST.get("authors").split(',') if len(item.rstrip().lstrip()) > 0])
    book_pagecount = int(request.POST.get("countpages"))
    book_language = str(request.POST.get("language"))
    book_picture = str(request.POST.get("linktopicture"))
    book_isbns = ([item.rstrip().lstrip() for item in request.POST.get("isbns").split(',') if len(item.rstrip().lstrip()) > 0])

    langid, created = models.Language.objects.get_or_create(langname=book_language)

    input_date = book_publisheddate.split("-")
    publish_date = date((int(input_date[0]) if len(input_date) > 1 else 2000),
                        (int(input_date[1]) if len(input_date) > 1 else 1),
                        (int(input_date[2]) if len(input_date) > 2 else 1))
    bookid, created = models.Book.objects.get_or_create(title=book_title,
                                                        langid=langid,
                                                        countpages=book_pagecount,
                                                        publishdate=publish_date,
                                                        defaults={'picture': book_picture})

    for author in book_authors:
        authorid, created = models.Author.objects.get_or_create(authorname=author)
        bookauthorid, created = models.Bookauthor.objects.get_or_create(authorid=authorid, bookid=bookid)

    for isbn in book_isbns:
        isbn, created = models.Isbnnumber.objects.get_or_create(isbn=isbn, bookid=bookid)

    return redirect("/")


def deleteBook(request):
    bookId = request.POST.get("delete-id")
    models.Isbnnumber.objects.filter(bookid=bookId).delete()
    models.Bookauthor.objects.filter(bookid=bookId).delete()
    models.Book.objects.get(id=bookId).delete()
    return redirect("/")


def editBook(request):
    book_id = int(request.POST.get("edit-id"))
    book_title = str(request.POST.get("title"))
    book_publisheddate = str(request.POST.get("publishdate"))
    book_authors = ([item.rstrip().lstrip() for item in request.POST.get("authors").split(',') if len(item.rstrip().lstrip()) > 0])
    book_pagecount = int(request.POST.get("countpages"))
    book_language = str(request.POST.get("language"))
    book_picture = str(request.POST.get("linktopicture"))
    book_isbns = ([item.rstrip().lstrip() for item in request.POST.get("isbns").split(',') if len(item.rstrip().lstrip()) > 0])

    models.Bookauthor.objects.filter(bookid=book_id).delete()
    models.Isbnnumber.objects.filter(bookid=book_id).delete()

    langid, created = models.Language.objects.get_or_create(langname=book_language)

    input_date = book_publisheddate.split("-")
    publish_date = date(
        (int(input_date[0]) if len(input_date) > 1 else 2000),
        (int(input_date[1]) if len(input_date) > 1 else 1),
        (int(input_date[2]) if len(input_date) > 2 else 1))
    models.Book.objects.filter(id=book_id).update(
        title=book_title,
        langid=langid,
        countpages=book_pagecount,
        publishdate=publish_date,
        picture=book_picture)
    book = models.Book.objects.get(id=book_id)

    for author in book_authors:
        authorid, created = models.Author.objects.get_or_create(authorname=author)
        bookauthorid, created = models.Bookauthor.objects.get_or_create(authorid=authorid, bookid=book)

    for isbn in book_isbns:
        isbn, created = models.Isbnnumber.objects.get_or_create(isbn=isbn, bookid=book)

    return redirect("/")
