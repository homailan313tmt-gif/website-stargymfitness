from django.contrib.admin import AdminSite, ModelAdmin
from reviews.models import(Publisher, Contributor, Book, BookContributor, Review)

class BookrAdminSite(AdminSite):
    title_header = 'Bookr Admin'
    site_header = 'Bookr administration'
    index_title = 'Bookr site admin'

admin_site = BookrAdminSite(name='bookr')

admin_site.register(Publisher)
admin_site.register(Contributor)
admin_site.register(BookContributor)
admin_site.register(Review)

class BookAdmin(ModelAdmin):
    list_display = ('title', 'isbn')

admin_site.register(Book, BookAdmin)