from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Memo


class MemoListView(LoginRequiredMixin, ListView):
    model = Memo
    template_name = 'memos/memo_list.html'
    context_object_name = 'memos'


class MemoDetailView(LoginRequiredMixin, DetailView):
    model = Memo
    template_name = 'memos/memo_detail.html'


class MemoCreateView(LoginRequiredMixin, CreateView):
    model = Memo
    fields = ['title', 'content']
    template_name = 'memos/memo_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MemoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Memo
    fields = ['title', 'content']
    template_name = 'memos/memo_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        memo = self.get_object()
        return self.request.user == memo.user


class MemoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Memo
    template_name = 'memos/memo_confirm_delete.html'
    success_url = reverse_lazy('memo-list')

    def test_func(self):
        memo = self.get_object()
        return self.request.user == memo.user