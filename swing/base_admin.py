from django.shortcuts import render, redirect


class BaseAdmin(object):
    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 10
    ordering = None
    filter_horizontal = []
    actions = ['delete_selected_objs', ]
    readonly_fields = []
    readonly_table = False
    modelform_exclude_fields = []
    add_form = None
    onclick_fields = []
    list_editable = []
    choice_fields = []
    fk_fields = []

    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        verbose_name = self.model._meta.verbose_name
        table_name = self.model._meta.model_name
        selected_ids = ','.join([str(i.id) for i in querysets])

        if self.readonly_table:
            errors = {'readonly_table': ' This table is read only,cannot be delete or edit.'}
        else:
            errors = {}

        if request.POST.get('_delete_confirm') == "yes":

            if not self.readonly_table:
                querysets.delete()
            return redirect('/swing/%s/%s/' % (app_name, table_name))
        return render(request, 'swing/table_obj_delete.html', {
                    'objs': querysets,
                    'admin_class': self,
                    'app_name': app_name,
                    'table_name': table_name,
                    'model_verbose_name': verbose_name,
                    'selected_ids': selected_ids,
                    "admin_action": request._admin_action,
                    'errors': errors})

    def default_form_validation(self):
        # 用户可以在此进行自定义的表单验证，相当于django form的clean方法
        pass


class AdminSite(object):
    def __init__(self, name='admin'):
        self.enabled_admins = {}  # model_class class -> admin_class instance

    def register(self, model_class, admin_class=None):
        if model_class._meta.app_label not in self.enabled_admins:
            self.enabled_admins[model_class._meta.app_label] = {}
        if not admin_class:  # no custom admin class , use BaseAdmin
            admin_class = BaseAdmin()
        admin_class.model = model_class  # 绑定model对象和admin 类
        self.enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class


site = AdminSite()
