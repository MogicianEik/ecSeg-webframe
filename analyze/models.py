from django.db import models
from django.contrib.auth.models import User
import os


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    org = models.CharField(
        'Organization', max_length=128, blank=True)

    telephone = models.CharField(
        'Telephone', max_length=50, blank=True)

    mod_date = models.DateTimeField('Last modified', auto_now=True)

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return self.user.__str__()


def get_image_rel_path(instance, filename):
    return '{}/{}'.format(str(instance.task.pk), filename)


task_status_choices = [
    (0, 'upload'),
    (1, 'process'),
    (2, 'success'),
    (3, 'fail'),
    ]


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)

    status = models.IntegerField(default=0, choices=task_status_choices)
    # 0 new task, and welcome to upload a image file
    # 1 indicates under processing
    # 2 process is successful
    # 3 task failed
    # we only need this

    @property
    def status_en(self):
        def translate_code(code):
            if code == 0:
                return 'New Task'
            elif code == 1:
                return 'Under Processing'
            elif code == 2:
                return 'Processed Successfully'
            elif code == 3:
                return 'Process Failed'
            else:
                return 'Unknown Status'
        return translate_code(self.status)

    @property
    def name_en(self):
        if self.name:
            return self.name
        else:
            return 'No Name'

    def to_json(self):
        return dict(
            id=self.pk,
            user_id=self.user.pk,
            task_id=self.pk,
            create_time=self.create_time,
            status=self.status
            )

    def __str__(self):
        return 'Task {}'.format(self.pk)


class Image(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    upload_time = models.DateTimeField('Upload Time', auto_now=True)
    image = models.ImageField(upload_to=get_image_rel_path)



