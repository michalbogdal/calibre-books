from haystack import indexes
from unidecode import unidecode

from .models import Book


class BookIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    genres = indexes.MultiValueField(null=True)

    def get_model(self):
        return Book

    def index_queryset(self, using=None):
        return self.get_model().objects.prefetch_related(
            'authors', 'comments', 'identifiers', 'languages')

    def prepare_genres(self, obj):
        return ','.join(obj.genres) or None

    def prepare(self, obj):
        self.prepared_data = super(BookIndex, self).prepare(obj)
        text = [obj.title, obj.isbn, obj.uuid]
        if obj.series:
            text.extend([obj.series])
        authors = [author.name for author in obj.authors.all()]
        authors.extend(map(unidecode, authors))
        text.extend(set(authors))
        text.extend(obj.tags.all())
        text.extend(obj.publishers.all())
        text.extend(['lang:%s' % l.lang_code for l in obj.languages.all()])
        text.extend(['publisher:%s' % p.name for p in obj.publishers.all()])
        self.prepared_data['text'] = u' '.join(map(unicode, text))
        return self.prepared_data
