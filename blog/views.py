from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.base import View
from igramscraper.instagram import Instagram
from .models import Post


instagram = Instagram()


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        tag = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        tags = tag.filter(title__icontains=search_query)
        return tags

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template_name'] = 'home'
        return context


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = Post.objects.get(id=self.get_object().id)
        context['medias'] = instagram.get_current_top_medias_by_tag_name(tag.title)
        context['tag_name'] = tag.title
        return context


class PostCreateView(CreateView):
    model = Post
    fields = ['title', ]

    def post(self, request, *args, **kwargs):
        tag_name = request.POST['tag_name']
        try:
            medias = instagram.get_current_top_medias_by_tag_name(tag_name)
            available_likes_counter = 0
            for media in medias:
                print(media.likes_count)
                if media.likes_count > 1000:
                    available_likes_counter += 1
            print(available_likes_counter)
            if available_likes_counter < 1:
                return render(request, 'blog/not_efficient_tag.html', {'template_name': 'create'})
            efficiency = 0
            for media in medias:
                likes_parametr = ((media.likes_count / 1000) * 11.1) / 10
                if likes_parametr > 11.1:
                    efficiency += 11.1
                else:
                    efficiency += likes_parametr
        except BaseException as e:
            print(e)
            return render(request, 'blog/not_efficient_tag.html', {'template_name': 'create'})
        tag = Post.objects.create(title=tag_name, efficient_percent=efficiency)
        tag.save()
        return redirect('blog-home')


class PostUpdateView(UpdateView):
    model = Post
    fields = ['title', ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template_name'] = 'update'
        tag = Post.objects.get(id=self.get_object().id)
        context['tag_name'] = tag.title
        return context

    def post(self, request, *args, **kwargs):
        tag_name = request.POST['tag_name']
        tag = Post.objects.get(id=self.get_object().id)
        try:
            medias = instagram.get_current_top_medias_by_tag_name(tag_name)
            available_likes_counter = 0
            for media in medias:
                if media.likes_count > 1000:
                    available_likes_counter += 1
            if available_likes_counter < 3:
                return render(request, 'blog/not_efficient_tag.html', {'template_name': 'update', 'post': tag})
            efficiency = 0
            for media in medias:
                likes_parametr = ((media.likes_count / 1000) * 11.1) / 10
                if likes_parametr > 11.1:
                    efficiency += 11.1
                else:
                    efficiency += likes_parametr
        except BaseException as e:
            print(e)
            return render(request, 'blog/not_efficient_tag.html', {'template_name': 'update', 'post': tag})
        tag = Post.objects.get(id=self.get_object().id)
        tag.title = tag_name
        tag.efficient_percent = efficiency
        tag.save()
        return redirect('blog-home')


class PostDeleteView(DeleteView):
    model = Post
    success_url = '/'


class PostStatistics(TemplateView):
    model = Post
    template_name = 'blog/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.all().order_by('-efficient_percent')
        if len(posts) < 3:
            context['enough_posts_to_analyze'] = False
            return context
        context['enough_posts_to_analyze'] = True
        context['posts'] = posts
        return context

def bad_request(request):
    return render(request, 'blog/not_efficient_tag.html')


