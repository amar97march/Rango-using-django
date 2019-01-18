from django.shortcuts import render
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list
    visitor_cookie_handler(request)
    context_dict['visits']=request.session['visits']

    #context_dict = {'boldmessage': "Crunchy, Creamy, Cookie, Candy, Cupcake"}
    response = render(request, 'rango/index.html', context=context_dict)


    return response

@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)

    return render(request,'rango/add_category.html',{'form':form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit= False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form':form,'category':category}
    return render(request,'rango/add_page.html',context_dict)



def show_category(request, category_name_slug):
    context_data = {}
    try:
        category = Category.objects.get(slug= category_name_slug)
        pages = Page.objects.filter(category = category)

        context_data['pages'] = pages
        context_data['category'] = category

    except category.DoesNotExist:
        context_data['category'] = None
        context_data['pages'] = None

    return render(request, 'rango/category.html', context_data)



def about(request):
    print(request.method)
    print(request.user)
    return render(request,'rango/about.html',{})

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data= request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.set_password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,'rango/register.html',{'user_form': user_form,'profile_form':profile_form,'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username = username, password= password)
        if user:
            if user.is_active:
                login(request, 'user')
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username,password))
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'rango/login.html',{})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def get_server_side_cookie(request, cookie, default_val= None):
    val = request.session.get(cookie)
    if not val:
        val= default_val
    return val

def visitor_cookie_handler(request):

    visits_cookie = int(get_server_side_cookie(request,'visits','1'))

    last_visit_cookie = get_server_side_cookie(request,'last_visit',str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')

    if (datetime.now()-last_visit_time).seconds > 0:
        visits = visits_cookie + 1

        request.session['last_visit'] = str(datetime.now())
    else:
        visits = visits_cookie
        request.session['last_visit']= last_visit_cookie

    request.session['visits'] = visits