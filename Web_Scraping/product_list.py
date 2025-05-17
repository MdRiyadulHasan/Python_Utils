from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from product.utils import scrape_product

def price_view(request):
    url = "https://burtprocess.com/ingersoll-rand-2175-283-gasket"  
    price_data = scrape_product(url)
    return render(request, 'product/price.html', {'price_data': price_data})