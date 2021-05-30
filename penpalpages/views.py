from django.shortcuts import render, redirect
from .forms import UserLoginForm, RegistrationForm, ProfileEditForm
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from django.contrib.auth import authenticate
# to show whether registration is successful or not we use messages from django.contrib
from django.contrib import messages
from .models import Profile, FriendRequest
from .utils import from_label_to_values, sort
from django.core.paginator import Paginator


# Create your views here.
def index(request):
    users = Profile.objects.all()
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        users = Profile.objects.exclude(user=request.user)
    else:
        profile = ''

    page_number = request.GET.get('page')
    paginator = Paginator(users, 4)
    page_object = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'page_object': page_object,
    }

    return render(request, 'penpalpages/index.html', context)


def search(request):
    query = request.GET.get('speaks').replace(" ", "")
    query2 = request.GET.get('learning').replace(" ", "")
    list_speaks = query.split(',')
    list_learning = query2.split(',')

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        results = Profile.objects.exclude(id=profile.id).filter(speaks__icontains=list_speaks[0]).filter(
            is_learning__icontains=list_learning[0])
    else:
        profile = ''
        results = Profile.objects.filter(speaks__icontains=list_speaks[0]).filter(
            is_learning__icontains=list_learning[0])

    results = sort(elements=list_speaks, results=results, lang_speaks=True)
    results = sort(elements=list_speaks, results=results, lang_learning=True)

    page_number = request.GET.get('page')
    paginator = Paginator(results, 4)
    page_object = paginator.get_page(page_number)

    search_string = f"speaks={request.GET.get('speaks')}&learning={request.GET.get('learning')}&"

    context = {
        'profile': profile,
        'page_object': page_object,
        'search_string': search_string,
    }

    return render(request, 'penpalpages/index.html', context)


def profile(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    friends = profile.friends.all()
    received_requests = FriendRequest.objects.filter(to_profile=profile)

    btn_text = ''
    if request.user.is_authenticated:
        if profile not in request.user.profile.friends.all():
            btn_text = 'not_friend'
            if len(FriendRequest.objects.filter(from_profile=request.user.profile).filter(to_profile=profile)) == 1:
                btn_text = 'request_sent'

    context = {
        'profile': profile,
        'btn_text': btn_text,
        'friends': friends,
        'received_requests': received_requests
    }
    return render(request, 'penpalpages/profile.html', context)


def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.speaks = form.from_values_to_labels('speaks')
            obj.is_learning = form.from_values_to_labels('is_learning')
            obj.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('penpalpages:profile', request.user.profile.id)
    else:
        is_learning = from_label_to_values(request, 'is_learning')
        speaks = from_label_to_values(request, 'speaks')
        form = ProfileEditForm(instance=request.user.profile, initial={'is_learning': is_learning, 'speaks': speaks})

    return render(request, 'penpalpages/edit.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login_user(request, user)
                return redirect('penpalpages:index')
            else:
                return redirect('penpalpages:login')

    else:
        form = UserLoginForm()
    # We're passing form into the template from code {'form': form}.
    return render(request, 'penpalpages/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # these messages will be linked to base template
            messages.success(request, 'Profile Successfully Created')
            return redirect('penpalpages:login')
        else:
            messages.error(request, 'Something went wrong!')

    else:
        form = RegistrationForm()

    return render(request, 'penpalpages/register.html', {'form': form})


def logout(request):
    # django has library which help in logout as below.
    logout_user(request)
    return redirect('penpalpages:login')


def send_request(request, to_profile_id):
    if request.user.is_authenticated:
        to_profile = Profile.objects.get(pk=to_profile_id)
        # get or create will save us from duplicate requests.
        frequest = FriendRequest.objects.get_or_create(
            from_profile=request.user.profile,
            to_profile=to_profile
        )

        return redirect('penpalpages:profile', profile_id=to_profile.id)


def cancel_request(request, to_profile_id):
    if request.user.is_authenticated:
        to_profile = Profile.objects.get(pk=to_profile_id)
        # get or create will save us from duplicate requests.
        f_request = FriendRequest.objects.filter(
            from_profile=request.user.profile,
            to_profile=to_profile
        ).first()
        f_request.delete()

        return redirect('penpalpages:profile', profile_id=to_profile.id)


def accept_friend_request(request, from_profile_id):
        from_profile = Profile.objects.get(pk=from_profile_id)
        # get or create will save us from duplicate requests.
        f_request = FriendRequest.objects.filter(
            from_profile=from_profile,
            to_profile=request.user.profile
        ).first()
        p1 = f_request.to_profile
        p2 = from_profile
        p1.friends.add(p2)
        # print(f_request)
        f_request.delete()

        return redirect('penpalpages:profile', profile_id=p1.id)


def delete_friend_request(request, from_profile_id):
    from_profile = Profile.objects.get(pk=from_profile_id)
    # get or create will save us from duplicate requests.
    f_request = FriendRequest.objects.filter(
        from_profile=from_profile,
        to_profile=request.user.profile
    ).first()

    f_request.delete()

    return redirect('penpalpages:profile', profile_id=request.user.profile.id)

def unfriend(request, profile_id):
    profile_to_unfriend = Profile.objects.get(id=profile_id)
    profile = request.user.profile
    # many to many fields are symmetrical
    profile.friends.remove(profile_to_unfriend)
    return redirect('penpalpages:profile', profile_id=profile.id)

