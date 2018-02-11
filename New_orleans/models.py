from swing import auth
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class Customer(models.Model):
    # 储存客户信息
    qq = models.CharField(max_length=64, unique=True, help_text=u'qq是唯一标识')
    name = models.CharField(u'姓名', max_length=32, null=True, blank=True, help_text=u'注册后请改为真实名字')
    qq_name = models.CharField(u'QQ名称', max_length=64, null=True, blank=True)
    phone = models.CharField(u'手机号', max_length=64, null=True, blank=True)
    birthday = models.DateField(u'出生日期', max_length=64, blank=True, null=True, help_text="格式yyyy-mm-dd")
    email = models.EmailField(u'常用邮箱', blank=True, null=True)
    id_num = models.CharField(u'身份证号', blank=True, null=True, max_length=64)

    sex_type = (('male', u'男'),
                ('female', u'女'))
    sex = models.CharField(u"性别", choices=sex_type, default='male', max_length=32)
    source_choices = (('referral', u'转介绍'),
                      ('qq', u'QQ群'),
                      ('web', u'官网'),
                      ('bd_ad', u'百度推广'),
                      ('51cto', u'51CTO'),
                      ('zhihu', u'知乎推广'),
                      ('market', u'市场推广'),
                      ('other', u'其他'),
                      )
    source = models.CharField(u'客户来源',
                              choices=source_choices,
                              max_length=64,
                              default=qq)
    status_choices = ((0, '已报名'),
                      (1, '未报名'),)
    status = models.PositiveSmallIntegerField(choices=status_choices, default=1)
    referral_from = models.CharField(verbose_name='转介绍人qq', max_length=64, null=True, blank=True)
    content = models.TextField(verbose_name='咨询详情')
    date = models.DateTimeField(auto_now_add=True)
    memo = models.TextField(blank=True, null=True)

    consultant = models.ForeignKey('UserProfile')
    consult_course = models.ForeignKey('Course', verbose_name='咨询课程')
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.qq

    class Meta:
        verbose_name = '客户表'


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '标签表'


class CustomerFollowUp(models.Model):
    content = models.TextField(verbose_name='跟进内容')
    consultant = models.ForeignKey('UserProfile')
    date = models.DateTimeField(auto_now_add=True)
    intention_choices = ((0, '2周内报名'),
                         (1, '1个月内报名'),
                         (2, '近期无报名计划'),
                         (3, '已在其他机构报名'),
                         (4, '已报名'),
                         (5, '已拉黑'),
                         )
    intention = models.SmallIntegerField(choices=intention_choices)
    customer = models.ForeignKey('Customer')

    def __str__(self):
        return '<%s : %s>' % (self.customer.qq, self.intention)

    class Meta:
        verbose_name_plural = '客户跟踪表'


class Branch(models.Model):
    # 储存校区信息
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '校区'
        verbose_name_plural = '校区'


class Course(models.Model):
    # 储存开设课程信息
    name = models.CharField(u'课程名称', unique=True, max_length=64)
    price = models.PositiveSmallIntegerField('价格')
    period = models.PositiveSmallIntegerField('课程周期(月)')
    outline = models.TextField('课程大纲')
    description = models.TextField("课程描述")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'


class ClassList(models.Model):
    # 储存班级信息
    class_type_choices = ((0, '面授班(脱产)'),
                          (1, '面授班(周末)'),
                          (2, '网络班'),
                          )
    class_type = models.PositiveSmallIntegerField(u'班级类型',
                                                  choices=class_type_choices,
                                                  default=0)
    semester = models.PositiveSmallIntegerField(u'学期')
    start_date = models.DateField(u'开班日期')
    end_date = models.DateField(u'结业日期', blank=True, null=True)

    teachers = models.ManyToManyField('UserProfile', verbose_name=u'讲师')
    course = models.ForeignKey('Course', verbose_name=u'课程')
    branch = models.ForeignKey('Branch', verbose_name=u'校区')

    def __str__(self):
        return '%s - %s - %s' % (self.branch, self.course, self.semester)

    class Meta:
        unique_together = ('branch', 'course', 'semester')
        # 避免重复创建班级，校区+课程名+学期做联合唯一
        verbose_name = u'班级列表'
        verbose_name_plural = '班级列表'

    def get_student_num(self):
        # 自定义方法，反向查找每个班级学员的数量
        return "%s" % self.customer_set.select_related().count()
    get_student_num.short_description = u'学员数量'


class CourseRecord(models.Model):
    # 储存上课记录信息
    day_num = models.PositiveSmallIntegerField(u'节次',
                                               help_text="此处填写第几节课,请填数字")
    has_homework = models.BooleanField(u'本节课程有作业', default=True)
    homework_title = models.CharField(u'作业标题', max_length=128, blank=True, null=True)
    homework_requirement = models.TextField(u'作业要求', blank=True, null=True)
    outline = models.TextField(u'本节课程大纲')
    date = models.DateField(u'上课日期', auto_now_add=True)

    from_class = models.ForeignKey('ClassList', verbose_name='班级')
    teachers = models.ForeignKey('UserProfile')

    def __str__(self):
        return '%s - 第%s节' % (self.from_class, self.day_num)

    class Meta:
        unique_together = ('from_class', 'day_num')
        verbose_name = '上课纪录'
        verbose_name_plural = '上课纪录'


class StudyRecord(models.Model):
    # 储存学员的成绩和出勤状况
    attendance_choices = ((0, '已签到'),
                          (1, '迟到'),
                          (2, '缺勤'),
                          (3, '早退'),
                          )
    score_choices = ((100, 'A+'),
                     (90, 'A'),
                     (85, 'B+'),
                     (80, 'B'),
                     (75, 'B-'),
                     (70, 'C+'),
                     (60, 'C'),
                     (40, 'C-'),
                     (-50, 'D'),
                     (-100, 'COPY'),
                     (0, 'N/A'),
                     )
    score = models.SmallIntegerField(choices=score_choices)
    attendance = models.SmallIntegerField(choices=attendance_choices, default=0)
    date = models.DateField(auto_now_add=True)
    memo = models.TextField(blank=True, null=True)

    student = models.ForeignKey('Enrollment')
    course_record = models.ForeignKey('CourseRecord')

    def __str__(self):
        return '%s - %s - %s' % (self.student, self.course_record, self.score)

    class Meta:
        verbose_name_plural = '学习记录表'


class UserProfile(AbstractBaseUser, PermissionsMixin):    # 账号表(自定义用户认证)
    email = models.EmailField(
        verbose_name='email address',
        max_length=64,
        unique=True,
    )
    password = models.CharField(_('password'), max_length=128,
                                help_text=mark_safe("<a href='password/'>修改密码</a>"))
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        verbose_name='staff status',
        default=True,
        help_text='Designates whether the user can log into this admin site.',
    )
    name = models.CharField(max_length=32)
    roles = models.ManyToManyField('Role', blank=True)
    branch = models.ForeignKey("Branch",
                               verbose_name="所属校区",
                               blank=True,
                               null=True)
    memo = models.TextField('备注', blank=True, null=True, default=None)
    date_joined = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    # stu_account = models.ForeignKey('Customer', verbose_name='关联学生账号',
    #                                 blank=True,
    #                                 null=True,
    #                                 help_text='只有学员报名后可为其创建账户')

    objects = auth.UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_superuser(self):
        return self.is_admin

    class Meta:
        verbose_name = '账户'
        verbose_name_plural = '账户'

        permissions = (
            ('crm_customers', '可以访问 客户库'),
            ('crm_table_list', '可以访问 kingadmin 每个表的数据列表页'),
            ('crm_table_index', '可以访问 kingadmin 首页'),
            ('crm_table_list_view', '可以访问 kingadmin 每个表中对象的修改页'),
            ('crm_table_list_change', '可以修改 kingadmin 每个表中对象'),
            ('crm_table_list_action', '可以操作 每个表的 action 功能'),
            ('crm_can_access_my_clients', '可以访问 自己的 客户列表'),
        )


class Enrollment(models.Model):     # 报名表
    contract_agreed = models.BooleanField(default=False, verbose_name='学员已同意合同条款')
    contract_approved = models.BooleanField(default=False, verbose_name='合同已审核')
    date = models.DateTimeField(auto_now_add=True)

    enrolled_class = models.ForeignKey('ClassList', verbose_name='所报班级')
    customer = models.ForeignKey('Customer')
    consultant = models.ForeignKey('UserProfile', verbose_name='课程顾问')

    def __str__(self):
        return '%s %s' % (self.customer, self.enrolled_class)

    class Meta:
        unique_together = ('customer', 'enrolled_class')
        verbose_name_plural = '报名表'


class Payment(models.Model):     # 缴费记录
    amount = models.PositiveIntegerField(default=500, verbose_name='数额')
    consultant = models.ForeignKey('UserProfile')
    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey('Customer')
    course = models.ForeignKey('Course', verbose_name='所报课程')

    def __str__(self):
        return '%s %s' % (self.customer, self.amount)

    class Meta:
        verbose_name_plural = '缴费表'


class Role(models.Model):
    name = models.CharField(max_length=32, unique=True)
    menus = models.ManyToManyField('Menu', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '角色表'


class Menu(models.Model):
    name = models.CharField(max_length=32)
    url_name = models.CharField(max_length=64)
    url_type_choices = ((0, 'alias'), (1, 'absolute_url'))
    url_type = models.SmallIntegerField(choices=url_type_choices, default=0)

    def __str__(self):
        return self.name
