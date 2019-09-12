from django.urls import path

from . import views

app_name = 'analyze'

urlpatterns = [
    path('logout', views.logout, name='logout'),
    path("login", views.login, name='login'),
    path("register", views.register, name="register"),
    path("get_current_task", views.get_current_task, name='get_current_task'),
    path("image_upload", views.image_upload, name='image_upload'),
    path("new_task", views.new_task, name='new_task'),
    path('del_image', views.del_image, name='del_image'),
    path('edit_task/<int:task_id>', views.edit_task, name='edit_task'),
    path('update_task_name/<int:task_id>', views.update_task_name, name='update_task_name'),
    path('list_task', views.list_task, name='list_task'),
    path('view_task/<int:task_id>', views.view_task, name='view_task'),
    path('start_process/<int:task_id>', views.start_process, name='start_process'),
    path('check_task_status/<int:task_id>', views.check_task_status, name='check_task_status'),
    path('batch_download/<int:task_id>', views.batch_download, name='batch_download'),
    path("", views.index, name="index")
]
