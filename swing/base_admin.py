from swing import models
from django.shortcuts import render, redirect, HttpResponse

enable_admins = {}
# 仿写admin.py，观察页面，推测，构造字典
# {'crm' : {'UserProfile': admin_class,
#           'customer': customer_admin}}


class BaseAdmin(object):
    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 5
    ordering = None
    filter_horizontal = []
    actions = ['delete_selected_objs', ]
    readonly_fields = []
    readonly_table = False
    modelform_exclude_fields = []

    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        action = request._admin_action
        selected_ids = ','.join([str(i.id) for i in querysets])  # 列表生成式

        if self.readonly_table:
            errors = {'readonly_table': ' This table is read only,cannot be delete or edit.'}
        else:
            errors = {}

        if request.POST.get('delete_confirm') == "yes":
            if not self.readonly_table:
                querysets.delete()
            return redirect('/snowball/%s/%s/' % (app_name, table_name))
        return render(request, 'snowball/snowball_obj_delete.html', {
                    'objs': querysets,
                    'admin_class': self,
                    'app_name': app_name,
                    'table_name': table_name,
                    'selected_ids': selected_ids,
                    'action': action,
                    'errors': errors})

    def default_form_validation(self):
        # 用户可以在此进行自定义的表单验证，相当于django form的clean方法
        pass


class CustomerAdmin(BaseAdmin):
    # model = models.Customer   # 绑定类属性
    list_display = ('id', 'qq', 'name', 'source', 'consultant', 'consult_course', 'date', 'status', 'enroll')
    list_filter = ('source', 'consultant', 'consult_course', 'status', 'date')
    search_fields = ('qq', 'name', 'consultant__name')  # consultant是个外键
    list_per_page = 5
    ordering = 'id'
    filter_horizontal = ('tags',)
    # readonly_fields = ['qq', 'consultant', 'tags']
    # readonly_table = True

    def enroll(self):   # 前端显示在数据库中不存在的用户自定义字段
        if self.instance.status == 0:
            link_name = 'Enroll new course'
        else:
            link_name = 'Enroll'
        return "<a href='/crm/customers/%s/enrollment/'>%s</a>" % (self.instance.id, link_name)

    enroll.display_name = '报名链接'

    def default_form_validation(self):
        # 用户可以在此进行自定义的表单验证，相当于django form的clean方法
        consult_content = self.cleaned_data.get('content', '')
        if len(consult_content) < 15:
            return self.ValidationError(
                'Field %(field)s 咨询内容纪录不能少于15字符',
                code='invalid',
                params={'field': 'content'},
            )

    def clean_name(self):   # 单个字段验证
        if not self.cleaned_data['name']:
            self.add_error('name', 'cannot be null.')


class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ('customer', 'consultant', 'date')


class UserProfileAdmin(BaseAdmin):
    list_display = ('email', 'name')
    readonly_fields = ('password',)
    filter_horizontal = ('groups', 'user_permissions')
    modelform_exclude_fields = ('last_login', )


class CourseRecordAdmin(BaseAdmin):
    def initialize_studyrecords(self, request, queryset):
        if len(queryset) > 1:
            return HttpResponse('只能选择一个班级')
        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():
            new_obj_list.append(models.StudyRecord(
                student=enroll_obj,
                course_record=queryset[0],
                attendance=0,
                score=0,
            ))
        try:
            models.StudyRecord.objects.bulk_create(new_obj_list)
        except Exception as e:
            return HttpResponse('批量创建失败,请检查是否已存在相应记录')
            """
                低效的批量创建,因为调用了save(),触发了commit
                        StudyRecord.objects.get_or_create(
                student=enroll_obj,
                course_record=queryset[0],
                attendance=0,
                score=0,
            )
            """
        return redirect('/snowball/crm/studyrecord/?course_record=%s' % queryset[0].id)

    list_display = ('from_class', 'day_num', 'teachers', 'has_homework', 'homework_title', 'date')
    list_filter = ('from_class', 'teachers')
    actions = ['initialize_studyrecords', ]   # 自动做反射
    initialize_studyrecords.display_name = '初始化本节所有学员上课记录'


class StudyRecordAdmin(BaseAdmin):
    list_display = ('student', 'course_record', 'attendance', 'score', 'date')
    list_filter = ('course_record', 'attendance', 'score')
    list_editable = ('attendance', 'score')


def register(model_class, admin_class=None):
    if model_class._meta.app_label not in enable_admins:
        enable_admins[model_class._meta.app_label] = {}
    admin_class.model = model_class     # 绑定model对象和admin类属性
    # admin_obj = admin_class()
    # admin_obj.model = model_class
    enable_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class


register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)
register(models.UserProfile, UserProfileAdmin)
register(models.CourseRecord, CourseRecordAdmin)
register(models.StudyRecord, StudyRecordAdmin)
