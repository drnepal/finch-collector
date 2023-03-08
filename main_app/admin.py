
from django.contrib import admin
# import your models here
from .models import Finch, Feeding, Toy, Photo

# Register your models here.
admin.site.register(Finch)
# register our new feeding model
admin.site.register(Feeding)

admin.site.register(Toy)
admin.site.register(Photo)