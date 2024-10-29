from rest_framework import serializers
from .models import Restaurant, Category, Product, ProductVariant, Order, OrderItem



class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['name', 'price']  # Remove gst_percent if you don't need it in the response


class ProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    icon = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'description', 'variants', 'icon']

    def get_variants(self, obj):
        # Use ProductVariantSerializer to serialize the variants
        variants = ProductVariantSerializer(obj.productvariant_set.all(), many=True).data
        return {variant['name']: variant['price'] for variant in variants}
    




class CategorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['name', 'items']

    def get_items(self, obj):
        # Get products associated with this category
        products = Product.objects.filter(category=obj, resturant=self.context['restaurant'])
        return ProductSerializer(products, many=True, context=self.context).data




class RestaurantMenuSerializer(serializers.ModelSerializer):
    restaurantName = serializers.CharField(source='name')
    menu = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['restaurantName', 'menu']

    def get_menu(self, obj):
        categories = Category.objects.all()  # Get all categories
        return {"categories": CategorySerializer(categories, many=True, context={'restaurant': obj}).data}





class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_variant', 'quantity', 'price', 'total_price', 'gst']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order