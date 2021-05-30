from django.shortcuts import render


# Create your views here.
def inbox(request, profile_friend=None):
    profile = request.user.profile
    friends = profile.friends.all()

    context = {
        'profile':profile,
        'friends':friends,
    }

    return render(request,'conversations/inbox.html',context)