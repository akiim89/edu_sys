# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from .models import Company, Division, User


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        'duplicate_email': 'This email has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('name', 'email')
        field_classes = {'email':forms.EmailField}

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=-email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

class MyPermissionMixin:
    def has_change_permission(self, request, obj=None):
        import pdb; pdb.set_trace()
        user = request.user
        # Anonymous users can do nothing.
        if not user.is_authenticated:
            return False
        # Superusers can do anything.
        if user.is_superuser:
            return True
        # Non-staff users can't log into admin site.
        if not user.is_staff:
            return False
        # Now get specific.
        if obj is None:
            # Can they edit these types of objects "in general." I don't really know what that means.
            return False
        # Defer to the object itself
        return user.has_permission('change')
    
    def has_delete_permission(self, request, obj=None):
        import pdb;pdb.set_trace()
        return self.has_change_permission(request, obj)

    def has_add_permission(self, _request):
        # This depends on if the parameters of the object being added. For
        # example, they can only add employees to a division where they are an
        # editor.

        # TODO: Implement more precise checking in the add forms for the various
        # models, and also in the REST interface.
        import pdb;pdb.set_trace()
        return True

class DeletedListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('deleted')),
            ('no', _('not deleted')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value() == 'yes':
            return queryset.filter(deleted_at__isnull=False)
        if self.value() == 'no':
            return queryset.filter(deleted_at__isnull=True)

@admin.register(User)
class MyUserAdmin(AuthUserAdmin, MyPermissionMixin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (_('Permissions'), {'fields': ('deleted_at', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', )}),
    )
    list_display = ('name', 'email', 'is_superuser')
    search_fields = ['name', 'email']
    ordering = ('name','email')
    list_filter = ('is_staff', 'is_superuser', 'deleted_at', 'groups')
        

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin, MyPermissionMixin):
    pass


admin.site.register(Company)
