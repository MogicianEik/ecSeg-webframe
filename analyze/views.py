from django.shortcuts import render, redirect
import io
import zipfile
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

from django.contrib import auth

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage

from .models import UserProfile, Task
from . import models
from .forms import RegistrationForm, LoginForm, ImageUploadFrom

from .ai_function import time_consuming_task  # fake process
from .ai_function import ALLOWED_EXTENSION
import threading

from process import settings

import os


def register(request):
    next_page = request.GET.get('next')

    if request.user.is_authenticated and next_page:
        return HttpResponseRedirect(next_page)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']

            user = User.objects.create_user(username=username, password=password, email=email)

            user_profile = UserProfile(user=user)
            user_profile.save()

            return HttpResponseRedirect(reverse('analyze:login'))

    else:
        form = RegistrationForm()

    return render(request, 'registration.html', {'form': form})


def login(request):
    next_page = request.GET.get('next')

    if request.user.is_authenticated:
        if next_page:
            return HttpResponseRedirect(next_page)
        else:
            return HttpResponseRedirect(reverse('analyze:list_task'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('analyze:list_task'))

            else:
                messages.error(request, 'Wrong password. Please try again.')
                return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def logout(request):
    print('logout')
    auth.logout(request)
    return HttpResponseRedirect(reverse('analyze:login'))


@login_required
def index(request):
    return HttpResponseRedirect(reverse('analyze:list_task'))


@login_required
def image_upload(request):
    user = request.user
    if request.method == 'POST':
        form = ImageUploadFrom(request.POST, request.FILES)
        if form.is_valid():
            task = form.cleaned_data['task']
            image = form.cleaned_data['image']
            print(task, image, image.name)
            im = form.save()

            # fs = FileSystemStorage()
            # fn = fs.save(os.path.join(str(task_id), image.name), image)

            # im = models.Image.objects.create(
            #     task=task,
            #     name=image.name,
            #     # image=fn
            #     )
            # im.image.save(image.name, image)
            # im.save()
            return JsonResponse(dict(status='success', image_id=im.pk))
    else:
        form = ImageUploadFrom()

    return render(request, 'image_upload.html', context=dict(form=form))


def __current_task(user, status):
    if not isinstance(user, User):
        raise TypeError
    if not isinstance(status, int):
        raise TypeError
    if status not in [0, 1, 2, 3]:
        raise ValueError
    task = Task.objects.filter(user=user, status=0).first()
    if task is None:
        task = Task.objects.create(user=user)
        task.save()
    return task


@login_required
def get_current_task(request):
    user = request.user
    task = Task.objects.filter(user=user, status=0).first()
    if task is None:
        task = Task.objects.create(user=user)
        task.save()
        # return HttpResponse('uploaded')
    return JsonResponse(task.to_json())


@login_required
def new_task(request):
    user = request.user
    task = __current_task(user=user, status=0)
    print('new_task')
    print(task.image_set.count())
    for image in task.image_set.all():
        print(image.image.url)
    messages.info(request, 'hello')
    return render(request, 'new_task.html', context=dict(task=task, header='Create New Task'))


@login_required
def del_image(request):
    image_id = request.GET.get('id')
    if image_id is None:
        return JsonResponse(dict(status='error', msg='image id needed'))
    try:
        image_id = int(image_id)
    except (ValueError, TypeError):
        return JsonResponse(dict(status='error', msg='image id should be integer'))

    image = models.Image.objects.filter(pk=image_id).first()
    if image is None:
        return JsonResponse(dict(status='error', msg='image {} not exist'.format(image_id)))
    if image.task.user_id != request.user.id:
        return JsonResponse(dict(status='error', msg='unauthorised'))
    if image.task.status != 0:
        return JsonResponse(dict(status='error', msg='image can not be deleted'))
    else:
        image.image.delete()
        image.delete()
        return JsonResponse(dict(status='success', msg='image deleted'))


@login_required
def edit_task(request, task_id):
    print(task_id)
    task = models.Task.objects.filter(pk=task_id).first()
    if task is None:
        return HttpResponseNotFound('Task {} not exists'.format(task_id))
    if task.user_id != request.user.id:
        return HttpResponseNotAllowed('You have no right to Task {}'.format(task_id))
    if task.status != 0:
        return HttpResponseNotAllowed('Task {} can not be edited'.format(task_id))
    else:
        return render(request, 'new_task.html', context=dict(task=task, header='Edit Task {}'.format(task_id)))


@login_required
def update_task_name(request, task_id):
    name = request.GET.get('name')
    if name is None:
        return JsonResponse(dict(status='error', msg='a new name must be supplied'))
    elif len(name) < 3:
        return JsonResponse(dict(status='error', msg='a new name must be at least 3 chars'))
    elif len(name) > 128:
        return JsonResponse(dict(status='error', msg='a new name must be at most 128 chars'))

    task = models.Task.objects.filter(pk=task_id).first()
    if task is None:
        return JsonResponse(dict(status='error', msg='Task {} not exists'.format(task_id)))
    if task.user_id != request.user.id:
        return JsonResponse(dict(status='error', msg='You have no right to Task {}'.format(task_id)))
    if task.status != 0:
        return JsonResponse(dict(status='error', msg='Task {} can not be edited'.format(task_id)))
    task.name = name
    task.save()
    return JsonResponse(dict(status='success', msg='task name updated'))


@login_required
def start_process(request, task_id):
    task = models.Task.objects.filter(pk=task_id).first()
    if task is None:
        return JsonResponse(dict(status='error', msg='Task {} not exists'.format(task_id), code=1))
    if task.user_id != request.user.id:
        return JsonResponse(dict(status='error', msg='You have no right to Task {}'.format(task_id), code=2))
    if task.status != 0:
        return JsonResponse(dict(status='error', msg='Task {} can not be edited'.format(task_id), code=3))
    if task.image_set.count() < 1:
        return JsonResponse(dict(status='error', msg='This task does not have any pictures',  code=4))
    task.status = 1
    task.save()
    fp = os.path.join(settings.MEDIA_ROOT, str(task_id))
    t = threading.Thread(target=time_consuming_task, args=(fp, task_id, change_task_status))
    t.setDaemon(True)
    t.start()
    return JsonResponse(dict(status='success', msg='task {} is processing'.format(task_id)))


def change_task_status(task_id, code):
    '''chang a task status'''
    if not isinstance(task_id, int):
        raise TypeError('task id should be integer')
    if task_id < 1:
        raise ValueError('task id should be bigger than zero')
    if code not in (2, 3):
        raise ValueError('code can only be 2 or 3')
    task = models.Task.objects.filter(pk=task_id).first()
    if task is None:
        raise ValueError('task {} not exists'.format(task_id))
    if task.status != 1:
        raise ValueError('task status is not proper')

    task.status = code

    task.save()


@login_required
def list_task(request):
    user = request.user
    tasks = models.Task.objects.filter(user=user).order_by('-id').all()
    paginator = Paginator(tasks, 20)
    page = request.GET.get('page')

    try:
        task_ls = paginator.page(page)
    except PageNotAnInteger:
        task_ls = paginator.page(1)
    except EmptyPage:
        task_ls = paginator.page(paginator.num_pages)

    return render(request, 'task_list.html', context=dict(
        task_ls=task_ls, title='Task List -- Ai Analyze',
                                                          ))


@login_required
def view_task(request, task_id):
    task = models.Task.objects.filter(pk=task_id).first()
    if task is None:
        return HttpResponseNotFound('Task {} not exists'.format(task_id))
    if task.user_id != request.user.id:
        return HttpResponseNotAllowed('You have no right to Task {}'.format(task_id))
    if task.status not in [0, 1, 2, 3]:
        return HttpResponseNotAllowed('Task {} status is unknown'.format(task_id))

    labels_dir = os.path.join(settings.MEDIA_ROOT, str(task_id), 'labels')
    labels = get_allowed_images(task_id=task_id)

    messages.info(request, '{}'.format(labels_dir))

    # if task.status == 2:
    #     result_dir = os.path.join(settings.MEDIA_ROOT, str(task_id), 'labels')

    return render(request, 'view_task.html', context=dict(task=task, labels=labels))


def make_thumbnails(folder):
    if not isinstance(folder, str):
        raise TypeError
    if not os.path.exists(folder):
        return
    if not os.path.isdir(folder):
        return
    images = []
    for name in os.listdir(folder):
        _, _ext = os.path.splitext(name)
        if _ext.lower() in ALLOWED_EXTENSION:
            images.append(os.path.join(folder, name))
    pass


def get_allowed_images(task_id):
    if not isinstance(task_id, int):
        raise TypeError
    folder = os.path.join(settings.MEDIA_ROOT, str(task_id), 'labels')
    files = []
    if not os.path.exists(folder):
        return files
    if not os.path.isdir(folder):
        return files
    for name in os.listdir(folder):
        _, _ext = os.path.splitext(name)
        if _ext.lower() in ALLOWED_EXTENSION:
            files.append(
                {
                    'url': '{}/{}/labels/{}'.format(settings.MEDIA_URL, task_id, name),
                    'name': name
                    }
                )
    return files


@login_required
def check_task_status(request, task_id):
    task = models.Task.objects.filter(pk=task_id).first()
    if task is None:
        return JsonResponse(dict(status='error', msg='Task {} not exists'.format(task_id), code=-1))
    if task.user_id != request.user.id:
        return JsonResponse(dict(status='error', msg='You have no right to Task {}'.format(task_id), code=-2))
    status = None
    msg = None
    code = None
    if task.status == 0:
        status = 'success'
        msg = 'new task, you can edit or start process'
        code = 0
    elif task.status == 1:
        status = 'success'
        msg = 'your task in under processing'
        code = 1
    elif task.status == 2:
        status = 'success'
        msg = 'your task already successfully processed'
        code = 2
    elif task.status == 3:
        status = 'success',
        msg = 'your task failed'
        code = 3
    else:
        status = 'error'
        msg = 'unknown status'
        code = -3
    return JsonResponse(dict(status=status, code=code, msg=msg))


@login_required
def batch_download(request, task_id):
    task = models.Task.objects.filter(pk=task_id).first()
    if task is None:
        return HttpResponseNotFound('Task {} not exists'.format(task_id))
    if task.user_id != request.user.id:
        return HttpResponseNotAllowed('You have no right to Task {}'.format(task_id))
    if task.status != 2:
        return HttpResponseNotAllowed('Task {} is not ready'.format(task_id))
    folder = os.path.join(settings.MEDIA_ROOT, str(task_id), 'labels')

    os.chdir(folder)

    files = []
    if not os.path.exists(folder):
        return HttpResponseNotFound('Task {} results missing'.format(task_id))
    if not os.path.isdir(folder):
        return HttpResponseNotFound('Task {} results missing'.format(task_id))
    for name in os.listdir(folder):
        _, _ext = os.path.splitext(name)
        if _ext.lower() in ALLOWED_EXTENSION:
            files.append(
                name
                # os.path.join(folder, name)
                )
    if not files:
        return HttpResponseNotFound('Task {} results missing'.format(task_id))

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for f in files:
            backup_zip.write(f)  # u can also make use of list of filename location
        # and do some iteration over it
    response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=task-{}-labels.zip'.format(task_id)
    response['Content-Length'] = zip_io.tell()
    return response