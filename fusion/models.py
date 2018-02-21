from swing import auth
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class Customer(models.Model):
    # 储存客户信息
    qq = models.CharField(u'QQ', max_length=64, unique=True, help_text=u'qq是唯一标识')
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
    status = models.PositiveSmallIntegerField(u'状态', choices=status_choices, default=1)
    referral_from = models.ForeignKey('self',
                                      verbose_name=u"转介绍自学员",
                                      help_text=u"若此客户是转介绍自内部学员,请在此处选学员姓名",
                                      blank=True,
                                      null=True,
                                      related_name="internal_referral")
    content = models.TextField(verbose_name='咨询详情', blank=True, null=True)
    date = models.DateTimeField(u'记录时间', auto_now_add=True)
    memo = models.TextField(u'备注', blank=True, null=True)

    consultant = models.ForeignKey('UserProfile', verbose_name=u'咨询顾问')
    consult_course = models.ForeignKey('Course', verbose_name=u'咨询课程')

    def __str__(self):
        return u"QQ:%s - 姓名:%s" % (self.qq, self.name)

    class Meta:
        verbose_name = u'客户信息'
        verbose_name_plural = u'客户信息'


class CustomerFollowUp(models.Model):
    # 储存客户后续跟进信息
    content = models.TextField(u'跟进内容', blank=True, null=True)
    date = models.DateTimeField(u'跟进日期', auto_now_add=True)
    intention_choices = ((0, '2周内报名'),
                         (1, '1个月内报名'),
                         (2, '近期无报名计划'),
                         (3, '已在其他机构报名'),
                         (4, '已报名'),
                         (5, '已拉黑'),
                         )
    intention = models.SmallIntegerField(u'意向', choices=intention_choices)

    consultant = models.ForeignKey('UserProfile', verbose_name=u'跟踪顾问')
    customer = models.ForeignKey('Customer', verbose_name=u'所咨询客户')

    def __str__(self):
        return u'%s - %s' % (self.customer, self.intention)

    class Meta:
        verbose_name = u'客户跟进记录'
        verbose_name_plural = u"客户跟进记录"


class Branch(models.Model):
    # 储存校区信息
    name = models.CharField(u'名称', max_length=64, unique=True)

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
    outline = models.TextField('课程大纲', blank=True, null=True)
    description = models.TextField("课程描述", blank=True, null=True)

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
    outline = models.TextField(u'本节课程大纲', blank=True, null=True)
    date = models.DateField(u'上课日期', auto_now_add=True)

    from_class = models.ForeignKey('ClassList', verbose_name='班级')
    teachers = models.ForeignKey('UserProfile', verbose_name=u'讲师')

    def __str__(self):
        return '%s - 第%s节' % (self.from_class, self.day_num)

    class Meta:
        unique_together = ('from_class', 'day_num')
        verbose_name = '上课纪录'
        verbose_name_plural = '上课纪录'


class StudyRecord(models.Model):
    # 储存学员的成绩和出勤状况
    attendance_choices = (('checked', u'已签到'),
                          ('late', u'迟到'),
                          ('absence', u'缺勤'),
                          ('leave_early', u'早退'),
                          )
    attendance = models.CharField(u'出勤情况', choices=attendance_choices, default=0, max_length=32)
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
    score = models.SmallIntegerField(u'本节成绩', choices=score_choices)
    date = models.DateField(u'日期', auto_now_add=True)
    memo = models.TextField(u'备注', blank=True, null=True)

    student = models.ForeignKey('Customer', verbose_name=u'学员')
    course_record = models.ForeignKey('CourseRecord', verbose_name=u'学习记录')

    def __str__(self):
        return u'%s - 学员:%s - 成绩:%s' % (self.course_record, self.student, self.score)

    class Meta:
        verbose_name = u'学员学习纪录'
        verbose_name_plural = u"学员学习纪录"
        # 一个学员，在同一节课只可能出现一次
        unique_together = ('course_record', 'student')


class UserProfile(AbstractBaseUser, PermissionsMixin):
    # 储存账户信息(自定义用户认证)
    email = models.EmailField(
        verbose_name='email address',
        max_length=128,
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
    memo = models.TextField('备注', blank=True, null=True, default=None)
    date_joined = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    roles = models.ManyToManyField('Role', blank=True)
    branch = models.ForeignKey("Branch",
                               verbose_name="所属校区",
                               blank=True,
                               null=True)

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
            ('customers', '可以访问 客户库'),
            ('table_list', '可以访问 swing 每个表的数据列表页'),
            ('table_index', '可以访问 swing 首页'),
            ('table_list_view', '可以访问 swing 每个表中对象的修改页'),
            ('table_list_change', '可以修改 swing 每个表中对象'),
            ('table_list_action', '可以操作 每个表的 action 功能'),
            ('can_access_my_clients', '可以访问 自己的 客户列表'),
        )


class Enrollment(models.Model):
    # 存储学员报名的信息
    customer = models.ForeignKey('Customer', verbose_name=u'学员')
    school = models.ForeignKey('Branch', verbose_name='校区')
    # 选择班级，班级是关联课程的
    course_class = models.ForeignKey("ClassList", verbose_name="所报班级")

    contract_agreed = models.BooleanField("我已认真阅读完培训协议并同意全部协议内容")
    contract_approved = models.BooleanField("审批通过", help_text=u"在审阅完学员的资料无误后勾选此项,合同即生效")
    enrolled_date = models.DateTimeField(auto_now_add=True, auto_created=True,
                                         verbose_name="报名日期")
    memo = models.TextField('备注', blank=True, null=True)

    def __str__(self):
        return "%s - 课程:%s" % (self.customer, self.course_class)

    class Meta:
        verbose_name = '学员报名表'
        verbose_name_plural = "学员报名表"
        unique_together = ("customer", "course_class")
        # 客户 + 班级"的联合唯一是为了可以让一个客户可以报多个班级


class PaymentRecord(models.Model):
    # 储存缴费记录
    pay_type_choices = (('deposit', u"订金/报名费"),
                        ('tuition', u"学费"),
                        ('refund', u"退款"),
                        )
    pay_type = models.CharField(u'费用类型', choices=pay_type_choices, max_length=64, default="deposit")
    amount = models.PositiveIntegerField(default=500, verbose_name='金额')
    date = models.DateTimeField(u'交款日期', auto_now_add=True)
    note = models.TextField("备注", blank=True, null=True)

    consultant = models.ForeignKey('UserProfile', verbose_name=u'课程顾问')
    enrollment = models.ForeignKey("Enrollment", verbose_name=u'报名信息')

    def __str__(self):
        return '%s - 类型:%s - 金额:%s' % (self.enrollment.customer, self.pay_type, self.amount)

    class Meta:
        verbose_name = '缴费纪录'
        verbose_name_plural = "缴费纪录"


class Role(models.Model):
    # 储存角色信息
    name = models.CharField(u'名称', max_length=32, unique=True)
    menus = models.ManyToManyField('FirstLayerMenu', blank=True, verbose_name='菜单')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"


class FirstLayerMenu(models.Model):
    # 储存第一层侧边栏菜单
    name = models.CharField(u'一级菜单名', max_length=64)
    url_type_choices = ((0, 'related_name'), (1, 'absolute_url'))
    url_type = models.SmallIntegerField(u'URL类型', choices=url_type_choices, default=0)
    url_name = models.CharField(u'URL名', max_length=64, unique=True)
    order = models.SmallIntegerField(default=0, verbose_name='菜单排序', blank=True, null=True)

    sub_menus = models.ManyToManyField('SubMenu', blank=True, verbose_name='子菜单')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "第一层菜单"
        verbose_name_plural = "第一层菜单"


class SubMenu(models.Model):
    # 储存第二层侧边栏菜单
    name = models.CharField(u'二级菜单名', max_length=64)
    url_type_choices = ((0, 'related_name'), (1, 'absolute_url'))
    url_type = models.SmallIntegerField(u'URL类型', choices=url_type_choices, default=0)
    url_name = models.CharField(u'URL名', max_length=64, unique=True)
    order = models.SmallIntegerField(default=0, verbose_name='菜单排序')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "第二层菜单"
        verbose_name_plural = "第二层菜单"


class StuAccount(models.Model):
    # 存储学员账户信息
    password = models.CharField(u'密码', max_length=128)
    valid_start = models.DateTimeField("账户有效期开始", blank=True, null=True)
    valid_end = models.DateTimeField("账户有效期截止", blank=True, null=True)

    account = models.OneToOneField("Customer", verbose_name='客户')

    def __str__(self):
        return self.account.customer.name

    class Meta:
        verbose_name = "学员账户"
        verbose_name_plural = "学员账户"
