from django.contrib import admin
from django.utils.html import format_html
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import GenericImage, Restaurant, Menu


class GenericImageInline(GenericTabularInline):
    model = GenericImage
    extra = 0
    readonly_fields = ['image_preview']
    fields = ['image', 'image_preview', ]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit:cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "پیش‌نمایش عکس"


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    inlines = [GenericImageInline]
    fieldsets = (
        ('Restaurant Info', {
            'fields': ('name', 'description', 'address', 'phone', 'table', 'desk_chair')
        }),
        ('Owner Restaurant', {
            'fields': ('owner', 'status', 'is_open')
        }),
        ('Time Info', {
            'fields': ('start_of_working_hours', 'end_of_working_hours', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ['id', 'name', 'phone', 'owner_fullname','is_open', 'status', 'created_at']
    ordering = ('-created_at',)
    search_fields = ['name', 'owner__fullname']
    list_filter= ['is_open', 'created_at']

    def owner_fullname(self, obj):
        return f"{obj.owner.fullname}" if obj.owner else "-"
    owner_fullname.short_description = 'مالک'


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [GenericImageInline]
    list_display = ['id', 'title', 'is_available', 'restaurant_name', 'created_at']
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ['title', 'restaurant__name']

    def restaurant_name(self, obj):
        return obj.restaurant.name if obj.restaurant else "-"
    restaurant_name.short_description = 'رستوران'


@admin.register(GenericImage)
class GenericImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_preview', 'uploaded_at']
    ordering = ('uploaded_at',)
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit:cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'پیش‌نمایش'
