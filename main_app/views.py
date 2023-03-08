from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import Finch, Toy, Photo
from .forms import FeedingForm
import uuid #python package for creating unique identifiers
import boto3 #what we'll use to connect to s3
from django.conf import settings

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


AWS_ACCESS_KEY= settings.AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY= settings.AWS_SECRET_ACCESS_KEY
S3_BUCKET= settings.S3_BUCKET
S3_BASE_URL= settings.S3_BASE_URL


# temporary finches for building templates
# finches = [
#     {'name': 'Lolo', 'breed': 'tabby', 'description': 'furry little demon', 'age': 3},
#     {'name': 'Sachi', 'breed': 'calico', 'description': 'gentle and loving', 'age': 2},
#     {'name': 'Tubs', 'breed': 'ragdoll', 'description': 'chunky lil guy', 'age': 0},
# ]

# Create your views here.
# view functions match urls to code (like controllers in Express)
# define our home view function
def home(request):
    return render(request, 'home.html')

# about route
def about(request):
    return render(request, 'about.html')

# index route for finches
def finches_index(request):
    # just like we passed data to our templates in express
    # we pass data to our templates through our view functions
    # we can gather relations from SQL using our model methods
    finches = Finch.objects.all()
    return render(request, 'finches/index.html', { 'finches': finches })

# detail route for finches
# finch_id is defined, expecting an integer, in our url
def finches_detail(request, finch_id):
    finch = Finch.objects.get(id=finch_id)

    # first we'll get a list of ids of toys the finch owns
    id_list = finch.toys.all().values_list('id')
    # then we'll make a list of the toys the finch does not have
    toys_finch_doesnt_have = Toy.objects.exclude(id__in=id_list)
    # instantiate FeedingForm to be rendered in the template
    feeding_form = FeedingForm()
    return render(request, 'finches/detail.html', { 'finch': finch, 'feeding_form': feeding_form, 'toys': toys_finch_doesnt_have })

class FinchCreate(CreateView):
    model = Finch
    # the fields attribute is required for a createview. These inform the form
    # fields = '__all__'
    fields = ['name','breed', 'age', 'description']
    # we could also have written our fields like this:
    # fields = ['name', 'breed', 'description', 'age']
    # we need to add redirects when we make a success
    # success_url = '/finches/{finch_id}'
    # or, we could redirect to the index page if we want
    # success_url = '/finches'
    # what django recommends, is adding a get_absolute_url method to the model
    def form_valid(self, form):
    # Assign the logged in user (self.request.user)
     form.instance.user = self.request.user  # form.instance is the cat
    # Let the CreateView do its job as usual
     return super().form_valid(form)


class FinchUpdate(UpdateView):
    model = Finch
    # let's use custom fields to disallow renaming a finch
    fields = ['breed', 'description', 'age']

class FinchDelete(DeleteView):
    model = Finch
    success_url = '/finches/'

def add_feeding(request, finch_id):
    # create a ModelForm instance from the data in request.POST
    form = FeedingForm(request.POST)

    # we need to validate the form, that means "does it match our data?"
    if form.is_valid():
        # we dont want to save the form to the db until is has the finch id
        new_feeding = form.save(commit=False)
        new_feeding.finch_id = finch_id
        new_feeding.save()
    return redirect('detail', finch_id=finch_id)

def assoc_toy(request, finch_id, toy_id):
    Finch.objects.get(id=finch_id).toys.add(toy_id)
    return redirect('detail', finch_id=finch_id)

def unassoc_toy(request, finch_id, toy_id):
    Finch.objects.get(id=finch_id).toys.remove(toy_id)
    return redirect('detail', finch_id=finch_id)

# ToyList
class ToyList(ListView):
    model = Toy
    template_name = 'toys/index.html'

# ToyDetail
class ToyDetail(DetailView):
    model = Toy
    template_name = 'toys/detail.html'

# ToyCreate
class ToyCreate(CreateView):
    model = Toy
    fields = ['name', 'color']

    # define what the inherited method is_valid does(we'll update this later)
    def form_valid(self, form):
        # we'll use this later, but implement right now
        # we'll need this when we add auth
        # super allows for the original inherited CreateView function to work as it was intended
        return super().form_valid(form)

# ToyUpdate
class ToyUpdate(UpdateView):
    model = Toy
    fields = ['name', 'color']

# ToyDelete
class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys/'

# view for adding photos
def add_photo(request, finch_id):
    # photo-file will be the name attribute of our form input
    photo_file = request.FILES.get('photo-file', None)
    # use conditional logic to make sure a file is present
    if photo_file:
        # S3_BASE_URL
        # if present, we'll use this to create a reference to the boto3 client
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        # create a unique key for our photos
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # we're going to use try....except which is just like try...finchch in js
        # to handle the situation if anything should go wrong
        try:
            # if success
            s3.upload_fileobj(photo_file, S3_BUCKET, key)
            # build the full url string to upload to s3
            url = f"{S3_BASE_URL}{S3_BUCKET}/{key}"
            # if our upload(that used boto3) was successful
            # we want to use that photo lofinchion to create a Photo model
            photo = Photo(url=url, finch_id=finch_id)
            # save the instance to the db
            photo.save()
        except Exception as error:
            # print an error message
            print('Error uploading photo', error)
            return redirect('detail', finch_id=finch_id)
    # upon success redirect to detail page 
    return redirect('detail', finch_id=finch_id)
def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in via code
            login(request, user)
            return redirect('index')
    else:
        error_message = 'Invalid sign up - try again'
        # A bad POST or a GET request, so render signup.html with an empty form
        form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)
