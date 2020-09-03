from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(req, *args, **kwargs):
        if req.user.is_authenticated:
            return redirect("home")
        else:
            return view_func(req, *args, **kwargs)
    return  wrapper_func    


def allowed_user(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(req, *args, **kwargs):

            group = None
            if req.user.groups.exists():
                group = req.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(req, *args, **kwargs)
            else:
                return HttpResponse('You are not authorized to view this page')
        return wrapper_func
    return decorator


def admin_only(view_func):
    def wrapped_function(req, *args, **kwargs):
        group = None
        if req.user.groups.exists():
            group = req.user.groups.all()[0].name
        
        if group == 'customer':
            return redirect('user-page')
        
        if group == 'admin':
            return view_func(req, *args, **kwargs)
    return wrapped_function