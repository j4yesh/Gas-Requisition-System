from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.getData),
    path('user/add/',views.add_person),
    path('user/show/',views.get_all_person),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('alluser',views.getAllUser),
    path('request/submit',views.submitRequest),
    path('request/get',views.getRequi),
    path('request/attach/<str:reqid>', views.uploadFile, name='upload-file'),
    path('servitor/request',views.getRequiForServitor),
    path('user/<str:username>/', views.getUserByUsername, name='get-user-by-username'),
    path('servitor/selfappoint/<str:reqid>',views.appointServitor),
    path('servitor/status/<str:reqid>/<str:idx>',views.changeStatusForServitor)
    # path('logout/',views.logout,name='logout'),
    # path('dashboard/',views.dashboard,name='dashboard')

]