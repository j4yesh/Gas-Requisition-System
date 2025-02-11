from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.getData),
    path('user/add/',views.add_person),
    path('user/show/',views.get_all_person),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    # path('logout/',views.logout,name='logout'),
    # path('dashboard/',views.dashboard,name='dashboard')

]