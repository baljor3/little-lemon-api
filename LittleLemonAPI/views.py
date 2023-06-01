from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework import status , permissions ,generics
from django.contrib.auth.models import User, Group 
from rest_framework.authtoken.models import Token
from .serializer import *
from .permission import *
from django.core.paginator import Paginator, EmptyPage
from datetime import date
from decimal import Decimal


#Classes

class Adminchangegroup(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
       #group 9 is managers
       queryset = User.objects.all().filter(groups = 9)
       return queryset

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        user_object = get_object_or_404(User,username =username)

        m = Group.objects.get(name = 'manager')

        m.user_set.add(user_object)
        
        return JsonResponse(status =201, data ={"message":"added"})
    
class AdminAddMenuItem(generics.ListCreateAPIView):
    queryset =MenuItems.objects.all()
    serializer_class = MenuItemsSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'POST':
               permission_classes = [IsAdminUser]
        return [permissions() for permission in permission_classes]
    
    def get(self,request, *args, **kwargs):
        items = MenuItems.objects.all()
        category_name = request.query_params.get('category')
        to_price =request.query_params.get('to_price')
        perpage = request.query_params.get('perpage', default  =10)
        page = request.query_params.get('page',default =1)
        if category_name:
            items = items.filter(category__title = category_name)
        if to_price:
            items = items.filter(price__lte = to_price)

        paginator = Paginator(items, per_page=perpage)
        try:
            items= paginator.page(number=page)
        except EmptyPage:
            items =[]
        serialized_item = MenuItemsSerializer(items,many = True)
        return Response(serialized_item.data)


    def post(self, request, *args, **kwargs):
        data=request.data
        data.featured = False
        serializer_item = MenuItemsSerializer(data =data)
        serializer_item.is_valid(raise_exception=True)
        serializer_item.save()
        return Response(serializer_item.data, status.HTTP_201_CREATED)
    
class AdminAddCategory(generics.ListCreateAPIView):
    queryset =Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get_permissions(self):
          permission_classes = []
          if self.request.method == 'POST':
               permission_classes = [IsAdminUser]
          return [permission() for permission in permission_classes]
    
    
    def post(self, request, *args, **kwargs):
        serializer_item = CategorySerializer(data =request.data)
        try:
            CategorySerializer(Category.objects.get(title =request.data["title"]))
            return JsonResponse({"message":"Category already created"})
        except:
            pass
        serializer_item.is_valid(raise_exception=True)
        serializer_item.save()
        return Response(serializer_item.data)
    
class ManagerChangeitemofday(generics.RetrieveUpdateAPIView):
    queryset = MenuItems.objects.all()
    serializer_class = MenuItemsSerializer
    permission_classes = [IsManager]

    def put(self, request, *args, **kwargs):
        menu = MenuItems.objects.get(pk = self.kwargs['pk'])

        menu.featured = request.data["featured"]
        menu.save()
        return Response(request.data)
    
class ManagerAssignUsers(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
       #group 8 is deliverycrew
       queryset = User.objects.all().filter(groups = 8)
       return queryset

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        user_object = get_object_or_404(User,username =username)

        m = Group.objects.get(name = 'deliverycrew')

        m.user_set.add(user_object)
        
        return JsonResponse(status =201, data ={"message":"added"})
    
    
#TODO: Managers can assign orders to the delivery crew, 
class ManagerAssgintoOrder(generics.UpdateAPIView):
    queryset = order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        data= request.data
        user =get_object_or_404( User,username = data['username'],groups = 8)
        order.objects.filter(id = self.kwargs.get('pk')).update(delivery_crew = user.pk )
        return Response("object changed")
# The delivery crew can access orders assigned to them, 
# The delivery crew can update an order as delivered
class DeliverycrewOperations(generics.ListCreateAPIView):
    queryset = order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsDeliveryCrew]

    def get_queryset(self):
        queryset = order.objects.filter(delivery_crew = self.request.user.id)
        return queryset
    
    def post(self, request, *args, **kwargs):
        data = request.data
        ord = order.objects.filter(id = data['id'],delivery_crew = self.request.user.id)
        ord.update(status = data["status"])
        return Response("item status has been changed")




class CustomerRegisteration(generics.ListCreateAPIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = []
        return [permissions() for permission in permission_classes]

    def post(self, request, *args, **kwargs):
        serializer_item = CustomerSerializer(data =request.data)
        serializer_item.is_valid(raise_exception=True)
        serializer_item.save()
        return JsonResponse(status =201, data ={"message":"user {} created".format(str(request.data["username"]))})


class CustomerAddItem(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        return cart

    def post(self, request, *args, **kwargs):
        data = request.data
        item = get_object_or_404(MenuItems, id = data['menuitem'])
        data._mutable= True
        data["user"] = self.request.user.id
        data["unit_price"] = item.price
        price = int(data['quantity']) * item.price
        data["price"] = price
        cart = Cart.objects.filter(user = self.request.user, menuitem = data['menuitem'])
           
        if not cart:
            serializer_item = CartSerializer(data=data)
            serializer_item.is_valid(raise_exception= True)
            serializer_item.save()

            return Response(serializer_item.data)
        else:
            return Response("object in cart")
    
    def delete(self, request, *args, **kwargs):

        data = request.data
        item = Cart.objects.get( user = self.request.user.id, menuitem = data['menuitem'])
        item.delete()

        return Response("item has been deleted")
        
class PlaceOrder(generics.ListCreateAPIView):
    queryset = order.objects.all()
    serializer_class = OrderSerializer
    serializer_item_order_item = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    

    def post(self, request, *args, **kwargs):
        data = request.data
        cart =Cart.objects.filter(user =self.request.user.id)
        #cart=get_object_or_404(Cart, user =self.request.user.id)
        total = 0
        for i in cart:
            total = total + i.price
        data['user'] = self.request.user.id
        data['total'] = total
        data['date'] = date.today()
        serializer_item = OrderSerializer( data =data)
        serializer_item.is_valid(raise_exception=True)
        serializer_item.save()
        keyList = ["order","menuitem","quantity","unit_price","price"]
        datar =dict(zip(keyList, [None]*len(keyList)))
        for j in cart.values():
            datar["order"] = serializer_item.data["id"]
            datar["menuitem"] = j["menuitem_id"]
            datar["quantity"] = j["quantity"]
            datar["unit_price"] = j["unit_price"]
            datar["price"] = j["price"]

            serializer_item_order_item = OrderItemSerializer(data = datar)
            serializer_item_order_item.is_valid(raise_exception= True)
            serializer_item_order_item.save()
        cart.delete()
        
        return Response(serializer_item_order_item.data)
    


class ViewOrderItems(generics.ListAPIView):
    queryset = orderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        get_object_or_404(order,user = self.request.user.id, id = self.kwargs.get('pk'))
        queryset = orderItem.objects.filter(order = self.kwargs.get('pk'))
        return queryset
    


        




        


    

    





        





   


