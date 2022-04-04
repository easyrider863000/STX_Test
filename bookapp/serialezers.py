class BookSerialiser:
    @staticmethod
    def serialize(bookObj, authors, isbns):
        return {
            "id": bookObj.id,
            "title": bookObj.title,
            "publishdate": bookObj.publishdate,
            "countpages": bookObj.countpages,
            "lang": {
                "id": bookObj.langid.id,
                "langname": bookObj.langid.langname
            },
            "picture": bookObj.picture,
            "authors": [{"id": author.id,
                         "name": author.authorname} for author in authors],
            "isbns": [{"id": isbn.id, "name": isbn.isbn} for isbn in isbns]
        }
