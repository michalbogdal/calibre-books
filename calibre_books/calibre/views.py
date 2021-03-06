import logging

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.http import urlencode
from django.views.generic import ListView, RedirectView

from .forms import SearchForm
from .models import Book, Data

logger = logging.getLogger(__name__)


class BookListView(ListView):
    model = Book
    template_name = 'calibre/list.html'
    paginate_by = settings.PAGINATE_BY

    def get_queryset(self):
        qs = self.model.objects.for_user(self.request.user)
        qs = qs.prefetch_related(
            'authors', 'comments', 'identifiers', 'languages')
        search_form = SearchForm(data=self.request.GET or None)
        if search_form.is_valid():
            ids = search_form.search().values_list('pk', flat=True)
            qs = qs.filter(id__in=ids).order_by('-pubdate')
        if 'series' in self.request.GET:
            qs = qs.order_by('series_index')
        return qs

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['filters'] = urlencode({'q': self.request.GET.get('q', ''),
                                        'g': self.request.GET.get('g', '')},
                                       doseq=1)
        return context


class DownloadView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if not Book.objects.for_user(self.request.user).filter(
                data__id=self.kwargs.get('pk')).exists():
            raise Http404
        book_file = get_object_or_404(Data, pk=self.kwargs.get('pk'))
        logger.info(u"Book '%s' has been downloaded by the user '%s'",
                    book_file.book, self.request.user,
                    extra={'request': self.request})
        return book_file.download_url
