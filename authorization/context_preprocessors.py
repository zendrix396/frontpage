def auth_status(request):
    return {
        'authorized':request.user.is_authenticated
    }