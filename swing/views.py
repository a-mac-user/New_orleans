import re
import json
from swing import tables, forms
from swing.base_admin import site
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, HttpResponseRedirect, Http404, HttpResponse


def entry(request):
    return render(request, 'entry.html')


def acc_login(request):
    error = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            request.session.set_expiry(60*60)
            return HttpResponseRedirect(request.GET.get('next') if request.GET.get('next') else '/entry')
        else:
            error["error"] = 'Wrong username or password!'
    return render(request, 'login.html', {'error': error})


def acc_logout(request):
    logout(request)
    return redirect('/login')


@login_required
def swing_index(request):
    print('sdasdsaf', site.enabled_admins)
    return render(request, 'swing/swing_index.html', {'enabled_admins': site.enabled_admins})


@login_required
def app_tables(request, app_name):
    enabled_admins = {app_name: site.enabled_admins[app_name]}
    return render(request, 'swing/swing_index.html', {'enabled_admins': enabled_admins,
                                                      'current_app': app_name})


def batch_update(request, editable_data, admin_class):
    # 批量更新
    errors = []
    for row_data in editable_data:
        obj_id = row_data.get('id')
        try:
            if obj_id:
                print("editable data", row_data, list(row_data.keys()))
                obj = admin_class.model.objects.get(id=obj_id)
                model_form = forms.create_form(admin_class.model, list(row_data.keys()),
                                               admin_class, request=request, partial_update=True)
                form_obj = model_form(instance=obj, data=row_data)
                if form_obj.is_valid():
                    form_obj.save()
                else:
                    print("list editable form", row_data, form_obj.errors)
                    errors.append([form_obj.errors, obj])
        except KeyboardInterrupt as e:
            return False, [e, obj]
    if errors:
        return False, errors
    return True, []


@login_required(login_url="/swing/login")
def display_table_list(request, app_name, table_name, embed=False):
    """
    :param request:
    :param app_name:
    :param table_name:
    :param embed: 若此函数是被另一个view调用的，则embed=True,嵌入时可开启
    :return:
    """

    errors = []
    if app_name in site.enabled_admins:
        # print(enabled_admins[url])
        if table_name in site.enabled_admins[app_name]:
            admin_class = site.enabled_admins[app_name][table_name]

            if request.method == "POST":  # action 来了

                print(request.POST)

                editable_data = request.POST.get("editable_data")
                if editable_data:  # for list editable
                    editable_data = json.loads(editable_data)
                    # print("editable",editable_data)
                    res_state, errors = batch_update(request, editable_data, admin_class)
                    # if res_state == False:
                    #    #errors.append(error)

                else:  # for action
                    selected_ids = request.POST.get("selected_ids")
                    action = request.POST.get("admin_action")
                    if selected_ids:
                        selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
                    else:
                        raise KeyError("No object selected.")
                    if hasattr(admin_class, action):
                        action_func = getattr(admin_class, action)
                        request._admin_action = action
                        return action_func(admin_class, request, selected_objs)

            querysets = tables.table_filter(request, admin_class, admin_class.model)
            searched_querysets = tables.search_by(request, querysets, admin_class)
            order_res = tables.get_orderby(request, searched_querysets, admin_class)

            paginator = Paginator(order_res[0], admin_class.list_per_page)

            page = request.GET.get('page')
            try:
                table_obj_list = paginator.page(page)
            except PageNotAnInteger:
                table_obj_list = paginator.page(1)
            except EmptyPage:
                table_obj_list = paginator.page(paginator.num_pages)

            table_obj = tables.TableHandler(request,
                                            admin_class.model,
                                            admin_class,
                                            table_obj_list,
                                            order_res)

            return_data = {'table_obj': table_obj,
                           'app_name': app_name,
                           'paginator': paginator,
                           'errors': errors,
                           'enabled_admins': site.enabled_admins}
            if embed:
                return return_data
            else:
                return render(request, 'swing/model_obj_list.html', return_data)

    else:
        raise Http404("url %s/%s not found" % (app_name, table_name))


@login_required(login_url="/swing/login")
def table_change(request, app_name, table_name, obj_id, embed=False):
    # print("table change:",app_name,table_name ,obj_id)

    if app_name in site.enabled_admins:
        if table_name in site.enabled_admins[app_name]:
            admin_class = site.enabled_admins[app_name][table_name]
            # print(enabled_admins[table_name])
            obj = admin_class.model.objects.get(id=obj_id)
            # print("obj....change",obj)
            fields = []
            for field_obj in admin_class.model._meta.fields:
                if field_obj.editable:
                    fields.append(field_obj.name)

            for field_obj in admin_class.model._meta.many_to_many:
                fields.append(field_obj.name)
            # print('fields', fields)
            model_form = forms.create_form(admin_class.model, fields, admin_class, request=request)

            if request.method == "GET":
                form_obj = model_form(instance=obj)

            elif request.method == "POST":
                print("post:", request.POST)
                form_obj = model_form(request.POST, instance=obj)
                if form_obj.is_valid():
                    form_obj.validate_unique()
                    if form_obj.is_valid():
                        form_obj.save()

            return_data = {'form_obj': form_obj,
                           'model_verbose_name': admin_class.model._meta.verbose_name,
                           'model_name': admin_class.model._meta.model_name,
                           'app_name': app_name,
                           'admin_class': admin_class,
                           'enabled_admins': site.enabled_admins
                           }
            if embed:
                return return_data
            else:
                return render(request, 'swing/table_change.html', return_data)

    else:
        raise Http404("url %s/%s not found" % (app_name, table_name))


@login_required(login_url="/swing/login")
def table_del(request, app_name, table_name, obj_id):
    if app_name in site.enabled_admins:
        if table_name in site.enabled_admins[app_name]:
            admin_class = site.enabled_admins[app_name][table_name]
            obj = admin_class.model.objects.filter(id=obj_id)
            if request.method == "POST":
                delete_tag = request.POST.get("_delete_confirm")
                if delete_tag == "yes":
                    obj.delete()
                    return redirect("/swing/%s/%s/" % (app_name, table_name))

            if admin_class.readonly_table is True:
                return render(request, 'swing/table_obj_delete.html')
            return render(request, 'swing/table_obj_delete.html', {
                'model_verbose_name': admin_class.model._meta.verbose_name,
                'model_name': admin_class.model._meta.model_name,
                'model_db_table': admin_class.model._meta.db_table,
                'obj': obj,
                'app_name': app_name,
            })


@login_required(login_url="/swing/login")
def table_add(request, app_name, table_name):
    # print("request :",request.POST)
    if app_name in site.enabled_admins:
        if table_name in site.enabled_admins[app_name]:
            fields = []
            admin_class = site.enabled_admins[app_name][table_name]
            for field_obj in admin_class.model._meta.fields:
                if field_obj.editable:
                    fields.append(field_obj.name)
            for field_obj in admin_class.model._meta.many_to_many:
                fields.append(field_obj.name)
            if not admin_class.add_form:
                model_form = forms.create_form(admin_class.model,
                                               fields,
                                               admin_class,
                                               form_create=True,
                                               request=request)
            else:  # this admin has customized  creation form defined
                model_form = admin_class.add_form

            if request.method == "GET":
                form_obj = model_form()
            elif request.method == "POST":
                form_obj = model_form(request.POST)
                if form_obj.is_valid():
                    form_obj.validate_unique()
                    if form_obj.is_valid():
                        print("add form valid", form_obj.cleaned_data)
                        form_obj.save()
                        if request.POST.get('_continue') is not None:

                            redirect_url = '%s/%s/' % (re.sub("add/$", "change", request.path), form_obj.instance.id)
                            # print('redirect url',redirect_url)
                            return redirect(redirect_url)
                        elif request.POST.get("_add_another") is not None:
                            # print('add another form', form_obj)
                            form_obj = model_form()

                        else:  # return to table list page
                            if "_popup=1" not in request.get_full_path():
                                redirect_url = request.path.rstrip("/add/")
                                return redirect(redirect_url)
                            else:
                                print("pop up add windows....")
            return render(request,
                          'swing/table_add.html',
                          {'form_obj': form_obj,
                           'model_name': admin_class.model._meta.model_name,
                           'model_verbose_name': admin_class.model._meta.verbose_name,
                           'model_db_table': admin_class.model._meta.db_table,
                           'admin_class': admin_class,
                           'app_name': app_name,
                           'enabled_admins': site.enabled_admins
                           })

    else:
        raise Http404("url %s/%s not found" % (app_name, table_name))


@login_required(login_url="/swing/login")
def personal_password_reset(request):
    app_name = request.user._meta.app_label
    model_name = request.user._meta.model_name

    if request.method == "GET":
        change_form = site.enabled_admins[app_name][model_name].add_form(instance=request.user)
    else:
        change_form = site.enabled_admins[app_name][model_name].add_form(request.POST, instance=request.user)
        if change_form.is_valid():
            change_form.save()
            url = "/%s/" % request.path.strip("/password/")
            return redirect(url)

    return render(request, 'swing/password_change.html', {'user_obj': request.user,
                                                          'form': change_form})


@login_required(login_url="/swing/login")
def password_reset_form(request, app_name, table_db_name, user_id):
    user_obj = request.user._meta.model.objects.get(id=user_id)
    can_change_user_password = False
    if request.user.is_admin or request.user.id == user_obj.id:
        can_change_user_password = True

    if can_change_user_password:
        if request.method == "GET":
            change_form = site.enabled_admins[app_name][table_db_name].add_form(instance=user_obj)
        else:
            change_form = site.enabled_admins[app_name][table_db_name].add_form(request.POST, instance=user_obj)
            if change_form.is_valid():
                change_form.save()
                url = "/%s/" % request.path.strip("/password/")
                return redirect(url)

        return render(request, 'swing/password_change.html', {'user_obj': user_obj,
                                                              'form': change_form})

    else:
        return HttpResponse("Only admin user has permission to change password")
