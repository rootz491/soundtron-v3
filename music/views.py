from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View
from .models import Album, song
# import for user
from django.shortcuts import redirect  # it will redirect user whenever user will login.
from django.contrib.auth import authenticate, \
        login  # authenticate: take user name and password, login: attaches session ID to user.
from .forms import RegisterForm, LoginForm, SongForm, AlbumForm  # import Forms from forms.py
# to check if user is authentic.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout  # to logout.


# supported file types
AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']




# index page
#       show albums only belongs to certain user.

class IndexView(LoginRequiredMixin, generic.ListView):
        model = Album
        login_url = 'music:login'
        template_name = 'music/index.html'
        context_object_name = 'albums'

        def get_queryset(self):
                return Album.objects.filter(user=self.request.user)


# detailed page
#       show the detail of that album.

class DetailView(LoginRequiredMixin, generic.DetailView):
        login_url = 'music:login'
        model = Album
        template_name = 'music/detail.html'
        context_object_name = 'albumObj'


# create album
#       handles to requests:
#               1. GET: serve the form
#               2. POST: take user data and save data to DB.

class AlbumCreate(LoginRequiredMixin, generic.CreateView):
        login_url = 'music:login'
        model = Album
        fields = ['artist', 'album_title', 'genre', 'album_logo', 'artist_logo']

        def form_valid(self, form):
                form_obj = form.save(commit=False)
                form_obj.user = self.request.user
                form_obj.save()
                print(self.request.user.username)
                return super(AlbumCreate, self).form_valid(form)


# delete album
#       just take the album id and delete it already.

class AlbumDelete(LoginRequiredMixin, generic.DeleteView):
        login_url = 'music:login'
        model = Album
        success_url = reverse_lazy('music:index')


# update album
#       not sure, but also handle two requests:
#               1. GET: serve the form
#               2. POST: take user data and update the database.

class AlbumUpdate(LoginRequiredMixin, generic.UpdateView):
        login_url = 'music:login'
        model = Album
        fields = ['artist', 'album_title', 'genre', 'album_logo', 'artist_logo']

        def form_valid(self, form):
                album = form.save(commit=False)
                album.user = self.request.user
                album.save()
                return super(AlbumUpdate, self).form_valid(form)


# create song
#       not figured out yet, but also handle two requests:
#               1. GET: serve the form.
#               2. POST: take song data and store into database.
'''
class SongCreate(LoginRequiredMixin, CreateView):
        login_url = 'music:login'
        model = song
        fields = ['song_title', 'audio_file']

        def form_valid(self, form):
                new_song = form.save(commit=False)
                print(self.request.POST.keys())
                new_song.save()
                return super(SongCreate, self).form_valid(form)
'''

def SongCreate(request, album_id):
        form = SongForm(request.POST or None, request.FILES or None)
        album = get_object_or_404(Album, pk=album_id)
        if form.is_valid():
                albums_songs = album.song_set.all()
                # checking if song is present already
                for s in albums_songs:
                        if s.song_title == form.cleaned_data.get("song_title"):
                                context = {
                                        'album': album,
                                        'form': form,
                                }
                                return render(request, 'music/song_form.html', context)
                new_song = form.save(commit=False)
                new_song.album = album
                new_song.audio_file = request.FILES['audio_file']
                # checking for audio file type
                file_type = new_song.audio_file.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in AUDIO_FILE_TYPES:
                        context = {
                                'album': album,
                                'form': form,
                                'error_message': 'Audio file must be WAV, MP3, or OGG',
                        }
                        return render(request, 'music/song_form.html', context)

                # after all checks, saving the form.
                new_song.save()
                # return render(request, 'music/detail.html', {'albumObj': album})
                return HttpResponseRedirect(reverse('music:detail', args=({'albumObj': album})))

        context = {
                'album': album,
                'form': form,
        }
        return render(request, 'music/song_form.html', context)


# delete song
#       it should be simple. just delete the song.


# register user
#       again handle two requests:
#               1. GET: serve registration form.
#               2. POST: take data and register the user.

class UserRegister(View):
        form_class = RegisterForm
        template_name = 'music/registration_form.html'

        # display blank form
        def get(self, request):
                form = self.form_class(None)
                return render(request, self.template_name, {'form': form})

        # process form data
        def post(self, request):
                form = self.form_class(request.POST)

                if form.is_valid():
                        user = form.save(commit=False)
                        print(form)
                        # clean (normalize) the data.
                        username = form.cleaned_data['username']
                        password = form.cleaned_data['password']
                        # to change the password
                        user.set_password(
                                password)  # we use this function coz the password will be hashed and not the plain text.
                        user.save()
                        # at this point, user data is stored into database.

                        # return User object if the credentials are correct.
                        user = authenticate(username=username, password=password)

                        if user is not None:
                                if user.is_active:
                                        login(request, user)  # means user logged in
                                        return redirect('music:index')  # redirect user to index page.
                                        # login successful!

                # if form is not valid then,
                return render(request, self.template_name, {'form': form})


# login user
#       same as register, but less work.
#       just authenticate the user.

class UserLogin(View):
        form_class = LoginForm
        template_name = 'music/login_form.html'

        def get(self, request):
                form = self.form_class(None)
                return render(request, self.template_name, {'form': form})

        def post(self, request):
                form = self.form_class(request.POST)

                username = request.POST['username']
                password = request.POST['password']
                # authenticate
                user = authenticate(request, username=username, password=password)

                if user is not None:
                        if user.is_active:  # if user is not blocked.
                                login(request, user)
                                return redirect('music:index')

                # if failed authentication
                return render(request, self.template_name, {'form': form})


# logout user

class UserLogout(View):

        def get(self, request):
                logout(request)
                return redirect('music:login')
