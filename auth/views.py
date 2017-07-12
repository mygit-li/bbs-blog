from django.shortcuts import redirect


def check_login(f):    # 装饰器，用来进行登录验证
    def inner(req, *args, **kwargs):
        user = req.session.get('user_info')
        if not user:
            return redirect('/login/')
        return f(req, *args, **kwargs)
    return inner
