from django.db import models


class Author(models.Model):
    authorname = models.CharField(db_column='authorName', max_length=200)

    class Meta:
        managed = False
        db_table = 'author'


class Book(models.Model):
    title = models.CharField(max_length=200)
    publishdate = models.DateField(db_column='publishDate')
    countpages = models.IntegerField(db_column='countPages')
    langid = models.ForeignKey('Language',
                               models.DO_NOTHING, db_column='langId')
    picture = models.CharField(max_length=2048)

    class Meta:
        managed = False
        db_table = 'book'


class Bookauthor(models.Model):
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='bookId')
    authorid = models.ForeignKey(Author,
                                 models.DO_NOTHING, db_column='authorId')

    class Meta:
        managed = False
        db_table = 'bookauthor'


class Isbnnumber(models.Model):
    isbn = models.CharField(max_length=13)
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='bookid')

    class Meta:
        managed = False
        db_table = 'isbnnumber'


class Language(models.Model):
    langname = models.CharField(db_column='langName', max_length=50)

    class Meta:
        managed = False
        db_table = 'language'
