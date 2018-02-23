from sales import forms
from fusion import models
from fusion.my_admin import site
from swing import forms as swing_forms
from swing import views as swing_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, Http404


@login_required()
def sales_index(request):
    # 销售主页
    template_data = swing_views.display_table_list(request, 'fusion', 'customer', embed=True)
    if type(template_data) is dict:
        return render(request, 'sales/sales_index.html', template_data)
    else:  # 调用的视图可能出错了，返回了一个错误页面，这里不做处理，也直接返回
        return template_data


@login_required
def customers(request):
    # 客户库
    template_data = swing_views.display_table_list(request, 'fusion', 'customer', embed=True)
    if type(template_data) is dict:
        return render(request, 'sales/all_customers.html', template_data)
    else:
        return template_data


@login_required
def customer_change(request, customer_id):
    # 客户信息修改
    template_data = swing_views.table_change(request, 'fusion', 'customer', customer_id, embed=True)
    if type(template_data) is dict:
        return render(request, 'sales/customer_change.html', template_data)
    else:
        return template_data


@login_required
def my_customers(request):
    # 每个销售自己的客户列表
    template_data = swing_views.display_table_list(request, 'fusion', 'customer', embed=True)
    if type(template_data) is dict:
        return render(request, 'sales/my_customer.html', template_data)
    else:
        return template_data


@login_required
def sales_report(request):
    # 销售报表
    template_data = swing_views.display_table_list(request, 'fusion', 'customer', embed=True)
    if type(template_data) is dict:
        return render(request, 'sales/sales_report.html', template_data)
    else:
        return template_data


@login_required
def enrollment(request, customer_id):
    # 销售填基本信息初始化报名操作
    fields = []
    for field_obj in models.Enrollment._meta.fields:
        if field_obj.editable:
            fields.append(field_obj.name)
    # print('site.enabled_admins:',site.enabled_admins)

    customer_obj = models.Customer.objects.get(id=customer_id)
    model_form = swing_forms.create_form(models.Enrollment,
                                         fields,
                                         site.enabled_admins[models.Enrollment._meta.app_label][models.Enrollment._meta.model_name])

    form = model_form()
    response_msg = {}
    if request.method == "POST":
        if request.POST.get('paid_fee'):  # payment form
            # 交费纪录
            fields = []
            for field_obj in models.PaymentRecord._meta.fields:
                if field_obj.editable:
                    fields.append(field_obj.name)
            model_form = swing_forms.create_form(models.PaymentRecord,
                                                 fields,
                                                 site.enabled_admins[models.PaymentRecord._meta.db_table])

            form = model_form(request.POST)
            if form.is_valid():
                form.save()
                enroll_obj = form.instance.enrollment
                customer_obj.status = "signed"
                customer_obj.save()
                response_msg = {'msg': 'payment record got created,enrollment process is done',
                                'code': 4,
                                'step': 5,
                                }
            else:
                enroll_obj = None
            return render(request, 'sales/enrollment.html',
                          {'response': response_msg,
                           'payment_form': form,
                           'customer_obj': customer_obj,
                           'enroll_obj': enroll_obj})

        post_data = request.POST.copy()
        print("post:", request.POST)
        form = model_form(post_data)
        exist_enrollment_objs = models.Enrollment.objects.filter(customer=customer_obj,
                                                                 course_grade=request.POST.get('course_grade'))
        if exist_enrollment_objs:
            if exist_enrollment_objs.filter(contract_agreed=True):
                # 学生已填写完报名表
                enroll_obj = exist_enrollment_objs.get(contract_agreed=True)
                if enroll_obj.contract_approved or request.POST.get('contract_approved') == "on":
                    enroll_obj.contract_approved = True
                    enroll_obj.save()
                    if enroll_obj.paymentrecord_set.select_related().count() > 0:  # already has payment record
                        response_msg = {'msg': '已报名成功', 'code': 5, 'step': 6}
                        return render(request,
                                      'sales/enrollment.html',
                                      {'response': response_msg,
                                       'customer_obj': customer_obj})
                    else:
                        response_msg = {'msg': 'contract approved, waiting for payment record to be created',
                                        'code': 3,
                                        'step': 4}
                        # 交费纪录
                        fields = []
                        for field_obj in models.PaymentRecord._meta.fields:
                            if field_obj.editable:
                                fields.append(field_obj.name)

                        model_form = swing_forms.create_form(models.PaymentRecord,
                                                             fields,
                                                             site.enabled_admins[models.PaymentRecord._meta.db_table])

                        form = model_form()

                        return render(request, 'sales/enrollment.html',
                                      {'response': response_msg,
                                       'payment_form': form,
                                       'customer_obj': customer_obj,
                                       'enroll_obj': enroll_obj})
                else:
                    response_msg = {'msg': 'waiting for contract approval',
                                    'code': 2,
                                    'step': 3,
                                    'enroll_boj': enroll_obj}
                form = model_form(post_data, instance=enroll_obj)

            else:

                response_msg = {'msg': 'enrollment_form already exist',
                                'code': 1,
                                'step': 2,
                                'enroll_obj': exist_enrollment_objs[0],
                                }

            form.add_error('customer', '报名表已存在')
        # form.cleaned_data['customer'] = customer_obj

        if form.is_valid():
            form.save()
            response_msg = {'msg': 'enrollment_form created',
                            'enroll_obj': form.instance,
                            'code': 1,
                            'step': 2}
    else:
        response_msg = {'msg': 'create enrollment form', 'code': 0, 'step': 1}
    return render(request,
                  'sales/enrollment.html',
                  {'response': response_msg,
                   'enrollment_form': form,
                   'customer_obj': customer_obj,
                   })


def stu_enrollment(request, enrollment_id):
    # 学生填报名表
    enroll_obj = models.Enrollment.objects.get(id=enrollment_id)
    customer_form = forms.CustomerForm(instance=enroll_obj.customer)
    return render(request, 'sales/stu_enrollment.html', {'enroll_obj': enroll_obj,
                                                         'customer_form': customer_form})
