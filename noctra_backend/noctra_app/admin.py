from django.contrib import admin
from .models import *

# Register your models here
admin.site.register(UserProfile)
admin.site.register(Club)
admin.site.register(ClubProfile)
admin.site.register(Event)
admin.site.register(Feed)
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Follow)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Reservation)

# Custom admin panel titles
admin.site.site_header = 'Noctra Admin'
admin.site.site_title = 'Noctra Admin'
admin.site.index_title = 'Welcome to Noctra Admin'
