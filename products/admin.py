from functools import update_wrapper
from django.contrib import admin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ngettext, gettext as _
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from .models import Category, Product

csrf_protect_m = method_decorator(csrf_protect)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_filter = ['category__title']
    list_display = ['id', 'category', 'title', 'is_active']

    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.opts.app_label, self.opts.model_name

        return [
            path("partial/", wrap(self.partial_changelist_view), name="%s_%s_partialchangelist" % info),
        ] + super().get_urls()

    def partial_changelist_view(self, request, extra_context=None):
        app_label = self.opts.app_label
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied

        cl = self.get_changelist_instance(request)
        formset = cl.formset = None
        if cl.list_editable and self.has_change_permission(request):
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        actions = self.get_actions(request)

        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields["action"].choices = self.get_action_choices(request)
            media += action_form.media
        else:
            action_form = None

        selection_note_all = ngettext(
            "%(total_count)s selected", "All %(total_count)s selected", cl.result_count
        )
        context = {
            **self.admin_site.each_context(request),
            "module_name": str(self.opts.verbose_name_plural),
            "selection_note": _("0 of %(cnt)s selected") % {"cnt": len(cl.result_list)},
            "selection_note_all": selection_note_all % {"total_count": cl.result_count},
            "title": cl.title,
            "subtitle": None,
            "is_popup": cl.is_popup,
            "to_field": cl.to_field,
            "cl": cl,
            "media": media,
            "has_add_permission": self.has_add_permission(request),
            "opts": cl.opts,
            "action_form": action_form,
            "actions_on_top": self.actions_on_top,
            "actions_on_bottom": self.actions_on_bottom,
            "actions_selection_counter": self.actions_selection_counter,
            "preserved_filters": self.get_preserved_filters(request),
            **(extra_context or {}),
        }
        request.current_app = self.admin_site.name

        response = TemplateResponse(
            request,
            self.change_list_template
            or [
                "admin/%s/%s/change_list_partial.html" % (app_label, self.opts.model_name),
                "admin/%s/change_list_partial.html" % app_label,
                "admin/change_list_partial.html",
            ],
            context,
        )

        print(cl)

        response.headers['HX-Push-Url'] = cl.get_query_string(None, None)

        return response

# Register your models here.
