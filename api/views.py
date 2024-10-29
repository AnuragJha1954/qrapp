from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Restaurant,Order, OrderItem, ProductVariant, Category, Product
from .serializers import RestaurantMenuSerializer, OrderSerializer




@swagger_auto_schema(
    method='get',
    operation_description="Get restaurant menu by ID",
    responses={200: openapi.Response('Success', RestaurantMenuSerializer)},
    manual_parameters=[
        openapi.Parameter(
            'restaurant_id', openapi.IN_PATH, description="ID of the restaurant",
            type=openapi.TYPE_INTEGER, required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def restaurant_menu(request, id):
    try:
        restaurant = Restaurant.objects.get(id=id)
    except Restaurant.DoesNotExist:
        raise NotFound("Restaurant not found")

    categories = Category.objects.filter(product__resturant=restaurant).distinct()
    menu = {"categories": []}

    for category in categories:
        products = Product.objects.filter(category=category, resturant=restaurant)
        items = []
        
        for product in products:
            # Construct the absolute URL for the icon
            icon_url = request.build_absolute_uri(product.image.url) if product.image else None
            
            # Construct the variants with IDs
            variants = {
                variant.name: {
                    "price": variant.price,
                    "id": variant.id  # Include the variant ID
                }
                for variant in product.productvariant_set.all()
            }
            
            items.append({
                "name": product.name,
                "description": product.description,
                "variants": variants,
                "icon": icon_url
            })
        
        menu["categories"].append({
            "categoryName": category.name,
            "items": items
        })

    # Prepare final response
    response_data = {
        "restaurantName": restaurant.name,
        "menu": menu
    }
    
    return Response(response_data)






@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'address': openapi.Schema(type=openapi.TYPE_STRING, description='Delivery address'),
            'mode': openapi.Schema(type=openapi.TYPE_STRING, description='Payment mode (UPI or Cash Payment)'),
            'items': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'product_variant': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the product variant'),
                        'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of the product variant')
                    },
                    required=['product_variant', 'quantity']
                )
            )
        },
        required=['address', 'mode', 'items'],
        description="Place an order with the specified items."
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'order_number': openapi.Schema(type=openapi.TYPE_STRING, description='Unique order number')
            }
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='This field is required.', example='This field is required.'),
                'mode': openapi.Schema(type=openapi.TYPE_STRING, description='This field is required.', example='This field is required.'),
                'items': openapi.Schema(type=openapi.TYPE_STRING, description='Product variant and quantity are required.', example='Product variant and quantity are required.'),
            }
        ),
        404: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(type=openapi.TYPE_STRING, description='Error message for not found items.')
            }
        )
    },
    operation_description="Place an order with the specified items."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def place_order(request):
    data = request.data

    # Validate required fields
    required_fields = ['items']
    for field in required_fields:
        if field not in data:
            return Response({field: 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize total price and GST
    total_price = 0
    total_gst = 0
    items_data = []

    for item in data['items']:
        product_variant_id = item.get('product_variant')
        quantity = item.get('quantity', 1)

        if not product_variant_id or quantity <= 0:
            return Response({'items': 'Product variant and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_variant = ProductVariant.objects.get(id=product_variant_id)
            item_price = product_variant.price
            item_gst = item_price * (product_variant.gst_percent / 100)
            item_total_price = (item_price + item_gst) * quantity

            # Update totals
            total_price += item_total_price
            total_gst += item_gst * quantity

            items_data.append({
                'product_variant': product_variant,
                'quantity': quantity,
                'price': item_price,
                'total_price': item_total_price,
                'gst': item_gst,
            })
        except ProductVariant.DoesNotExist:
            return Response({'items': f'Product variant with id {product_variant_id} does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    # Create the Order instance
    order = Order.objects.create(
        order_number=generate_order_number(),  # Implement this function
        total_price=total_price,
        gst=total_gst,
        status='PENDING',
        order_date=timezone.now()
    )

    # Create OrderItem instances
    for item in items_data:
        OrderItem.objects.create(
            order=order,
            product_variant=item['product_variant'],
            quantity=item['quantity'],
            price=item['price'],
            total_price=item['total_price'],
            gst=item['gst'],
        )

    return Response({'error':False, 'message':'Your Order has been Placed successfully','order_number': order.order_number}, status=status.HTTP_201_CREATED)

def generate_order_number():
    # Implement your order number generation logic here
    import random
    import string
    order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return order_number