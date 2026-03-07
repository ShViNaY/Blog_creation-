from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name  = 'posts'
    ordering = ['-date_posted']    #newest first
    #  ordering = ['date_posted']    #oldest first

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
        return False
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    # success_url = '/'
    success_url = reverse_lazy('blog-home')

    def test_func(self):
            post = self.get_object()
            if self.request.user == post.author:
                return True
            return False
    
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


