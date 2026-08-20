from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
                                  ListView, 
                                  DetailView, 
                                  CreateView,
                                  UpdateView,
                                  DeleteView
                                  )
from django.urls import reverse_lazy
#Listview = Fetches data from a model, sends it to a template, displays it as a list
from django.http import HttpResponse
from .models import Post

# posts = [
#     {
#         'author' : 'CareyMS',
#         'title' : 'Blog Post 1',
#         'content' : 'First Post Content',
#         'date_posted' : 'August 27, 2018',
#     },
#     {
#         'author' : 'Jane Doe',
#         'title' : 'Blog Post 2',
#         'content' : 'Second Post Content',
#         'date_posted' : 'August 28, 2018',
#     }
# ]


class PostDetailView(DetailView):
    model = Post
    # template_name = 'blog/post_detail.html'
    # context_object_name  = 'posts'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    # success_url = '/'
    success_url = reverse_lazy('blog-home')

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False

from django.core.paginator import Paginator


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 2

    def get_context_data(self, **kwargs):
        """Produce a synthetic pagination where page 1 is the hero-only page
        and pages 2..(N+1) map to the real paginator pages 1..N. This makes
        "Latest Articles" on page 1 link to page 2 which will contain the
        newest posts.
        """
        # Build context manually to avoid Django's built-in pagination raising
        # an InvalidPage error before this method can run. This view implements
        # a synthetic pagination where page 1 is the hero page.
        context = {}
        context['view'] = self

        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        real_num_pages = paginator.num_pages
        synthetic_num_pages = real_num_pages + 1

        # Requested (synthetic) page number (keep original for messaging)
        try:
            orig_req = int(self.request.GET.get('page', '1'))
            if orig_req < 1:
                orig_req = 1
        except Exception:
            orig_req = 1

        # Clamp the requested synthetic page into the valid range [1, synthetic_num_pages]
        req_page = min(orig_req, synthetic_num_pages) if synthetic_num_pages >= 1 else 1

        class SimplePaginator:
            def __init__(self, num_pages):
                self.num_pages = num_pages
                self.page_range = range(1, num_pages + 1)

        class SimplePage:
            def __init__(self, number, paginator_obj, object_list):
                self.number = number
                self.paginator = paginator_obj
                self.object_list = object_list

            @property
            def has_previous(self):
                return self.number > 1

            @property
            def has_next(self):
                return self.number < self.paginator.num_pages

            def previous_page_number(self):
                return max(1, self.number - 1)

            def next_page_number(self):
                return min(self.paginator.num_pages, self.number + 1)

        synthetic_paginator = SimplePaginator(synthetic_num_pages)

        status_message = None
        if orig_req > synthetic_num_pages:
            # Inform the user they requested beyond the last page
            status_message = 'Reached the last page.'

        if req_page == 1:
            # Hero page: no posts displayed here
            page_obj = SimplePage(1, synthetic_paginator, [])
            object_list = []
            is_paginated = synthetic_num_pages > 1
        else:
            # Map synthetic page N to real page N-1
            real_page_num = max(1, req_page - 1)
            # Clamp to last real page if necessary
            real_page_num = min(real_page_num, real_num_pages) if real_num_pages > 0 else 1
            try:
                real_page = paginator.page(real_page_num) if real_num_pages > 0 else None
                object_list = real_page.object_list if real_page is not None else []
            except Exception:
                # Any issue reading a real page yields an empty result set
                object_list = []
            page_obj = SimplePage(req_page, synthetic_paginator, object_list)
            is_paginated = synthetic_num_pages > 1

        # Replace context entries that Django's ListView would normally set
        context['posts'] = object_list
        context['page_obj'] = page_obj
        context['paginator'] = synthetic_paginator
        context['is_paginated'] = is_paginated
        context['object_list'] = object_list
        if status_message:
            context['status_message'] = status_message
        return context

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, username = self.kwargs.get('username'))
        return Post.objects.filter(author = user).order_by('-date_posted')

    
def home(request):
    # return HttpResponse('<h1>Blog Home</h1>')
    # return render(request, 'blog/home.html')
    # context = {
    #     'posts':posts
    # }
    context = {
        'posts' : Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

def about(request):
    # return HttpResponse('<h1>Blog About</h1>')
    #  return render(request, 'blog/about.html')
     return render(request, 'blog/about.html', {'title': 'About'})


