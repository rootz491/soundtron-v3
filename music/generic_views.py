from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View
from .models import Album
# import for user
from django.shortcuts import redirect                   # it will redirect user whenever user will login.
from django.contrib.auth import authenticate, login     # authenticate: take user name and password, login: attaches session ID to user.
from .forms import RegisterForm, LoginForm, SongForm, AlbumForm    # import Forms from forms.py
# to check if user is authentic.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout                  # to logout.



AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']



class IndexView(LoginRequiredMixin, generic.ListView):
        login_url = 'music:login'
        template_name = 'music/index.html'
        context_object_name = 'albums'

        def get_queryset(self):
                # get all album as an object
                return Album.objects.filter(user=self.request.user)


class DetailView(LoginRequiredMixin, generic.DetailView):
        login_url = 'music:login'
        model = Album
        template_name = 'music/detail.html'
        context_object_name = 'albumObj'



class AlbumCreate(LoginRequiredMixin, View):
        login_url = 'music:login'
        form_class = AlbumForm
        template_name = 'music/album_form.html'

        def get(self, request):
                form = self.form_class(None)
                return render(request, self.template_name, {'form': form})

        def post(self, request):
                form = self.form_class(request.POST)

                if form.is_valid():
                        album = form.save(commit=False)

                        album.user = request.user
                        album.album_logo = request.FILES['album_logo']
                        album.artist_logo = request.FILES['artist_logo']
                        album.artist = request.POST['artist']
                        album.genre = request.POST['genre']
                        album.album_title = request.POST['album_title']
                        # file type of images is already set because model type.
                        album.save()
                        print('album saved')
                        return render('music:index')

                # if form is not valid, then again to
                return render(request, self.template_name, {'form': form})




class SongCreate(LoginRequiredMixin, View):
        login_url = 'music:login'
        form_class = SongForm
        template_name = 'music/song_form.html'

        def get(self, request):
                form = self.form_class(None)
                return render(request, self.template_name, {'form': form})

        def post(self, request):
                album = get_object_or_404(Album, pk=self.request.GET['pk'])
                form = self.form_class(request.POST)

                if form.is_valid():
                        albums_songs = album.song_set.all()
                        for s in albums_songs:
                                if s.song_title == form.cleaned_data.get("song_title"):
                                        context = {
                                            'album': album,
                                            'form': form,
                                            'error_message': 'You already added that song',
                                        }
                                        return render(request, self.template_name, context)

                        song = form.save(commit=False)
                        song.album = album
                        song.audio_file = request.FILES['audio_file']
                        # return to album page
                        return render('music:detail')

                return render(request, self.template_name, {'album': album, 'form': form})


class AlbumUpdate(LoginRequiredMixin, UpdateView):
        login_url = 'music:login'
        model = Album
        template_name = 'music/detail.html'
        fields = ['artist', 'album_title', 'genre', 'album_logo', 'artist_logo']

        def form_valid(self, form):
                form_obj = form.save(commit=False)
                form_obj.user = self.request.user
                form_obj.save()
                return super(AlbumUpdate, self).form_valid(form)


class AlbumDelete(LoginRequiredMixin, DeleteView):
        login_url = 'music:login'
        model = Album
        success_url = reverse_lazy('music:index')



# Handle user

# register handler
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
                        user.set_password(password)             # we use this function coz the password will be hashed and not the plain text.
                        user.save()
                        # at this point, user data is stored into database.


                        # return User object if the credentials are correct.
                        user = authenticate(username=username, password=password)

                        if user is not None:
                                if user.is_active:
                                        login(request, user)            # means user logged in
                                        return redirect('music:index')  # redirect user to index page.
                                        # login successful!

                # if form is not valid then,
                return render(request, self.template_name, {'form': form})


# login handler
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


# user logout
class UserLogout(View):

        def get(self, request):
                logout(request)
                return redirect('music:login')



