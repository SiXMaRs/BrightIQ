from django.shortcuts import render
from django.core.paginator import Paginator
from sklearnapp.models import SklearnModel
from django.views.generic import ListView

def home(req):
    page = req.GET.get('page', 1)
    paginate_by = req.GET.get('paginate_by', 10)
    object_list = SklearnModel.objects.order_by('name')
    paginator = Paginator(object_list, paginate_by)
    page_object = paginator.page(page)
    context = {
        'object_list' : object_list,
        'paginate_by': page,
        'paginator': paginator,
        'page_obj': page_object,

    }
    
    return render(req,'sklearnapp/home.html', context  )

class HomeListView(ListView):
    model = SklearnModel
    template_name = 'sklearnapp/home.html'
    paginate_by = 10
    