from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api-token-auth/', obtain_auth_token),
    path('adminchange/',views.Adminchangegroup.as_view()),
    path('admin-add-menu-item/', views.AdminAddMenuItem.as_view()),
    path('admin-add-category/', views.AdminAddCategory.as_view()),
    path('Manager-change/<pk>',views.ManagerChangeitemofday.as_view()),
    path('Manager-change-group/', views.ManagerAssignUsers.as_view()),
    path('UserRegister/',views.CustomerRegisteration.as_view()),
    path('Cart/',views.CustomerAddItem.as_view()),
    path('placeorder/',views.PlaceOrder.as_view()),
    path('OrderItems/<pk>', views.ViewOrderItems.as_view()),
    path('AssignOrder/<pk>',views.ManagerAssgintoOrder.as_view()),
    path('Deliverycrew/', views.DeliverycrewOperations.as_view())
]