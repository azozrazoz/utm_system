from django.contrib import messages

def notifications(request):
    success_messages = [m.message for m in messages.get_messages(request) if m.level_tag == 'success']
    error_messages = [m.message for m in messages.get_messages(request) if m.level_tag == 'error' or m.level_tag == 'danger']

    return {
        'success_messages': success_messages,
        'error_messages': error_messages,
    }