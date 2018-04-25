from urllib.parse import quote_plus
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Post
from .forms import PostForm
from django.utils import timezone

# Create your views here.


def post_create(request):
	if not request.user.is_staff or request.user.is_superuser:
		raise Http404

	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, 'Successfully saved!')
		return HttpResponseRedirect(instance.get_absolute_url())
	else:
		messages.error(request, 'Not successfully saved!')
	context = {
		'form':form,
	}
	return render(request, 'post_form.html', context)

def post_detail(request, slug):
	instance = get_object_or_404(Post, slug=slug)
	if instance.publish > timezone.now().date() or instance.draft:
		if not request.user.is_staff or request.user.is_superuser:
			raise Http404
	share_string = quote_plus(instance.content)
	context = {
		'title':instance.title,
		'instance':instance,
		'share_string':share_string,
	}  
	return render(request, 'post_detail.html', context)

def post_update(request, slug=None):
	if not request.user.is_staff or request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		messages.success(request, 'Itemed saved!')
		return HttpResponseRedirect(instance.get_absolute_url())
	context = {
		'title':instance.title,
		'instance':instance,
		'form':form,
	}
	return render(request, 'post_form.html', context)

def post_list(request):
	today = timezone.now().date()
	queryset_list = Post.objects.active() #.order_by("-timestamp")
	if request.user.is_staff or request.user.is_superuser:
		request_list = Post.objects.all()

	query = request.GET.get('q')
	if query:
		queryset_list = queryset_list.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)|
			Q(user__first_name__icontains=query)|
			Q(user__last_name__icontains=query)
			).distinct()
	paginator = Paginator(queryset_list, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		queryset = paginator.page(1)
	except EmptyPage:
		queryset = paginator.page(paginator.num_pages)

	context = {
		'object_data':queryset,
		'title':'list',
		'page_request_var': page_request_var,
		'today':today,
	}
	return render(request, 'post_list.html', context)

def post_delete(request, slug=None):
	if not request.user.is_staff or request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	instance.delete()
	messages.success(request, 'Successfully deleted')
	return redirect('posts:list')
	