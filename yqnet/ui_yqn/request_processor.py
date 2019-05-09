# Common request processor

from django.http.response import HttpResponse
from django.template.response import TemplateResponse

def maybe_redirect(get_response):

    def middleware(request):

	# We're coming from the Custom Tab from Android webapp which spawned it
	# do to the oauth to google. We need to return the request back to the
	# webapp so have to intercept it and send it on to the app.
	# This will be something like https://example.com/oauth/oauth-google/?tokens=example
	# Which will then be passed to the app via AppCustomUri://oauth/oauth-google/?token=example
	# It would be nice if we could do a redirect but that is not permitted in custom tabs on android

        if 'HTTP_X_QUAKR_ORIGIN' in request.META and "oauth" in request.path:
            link = 'quakr://%s?%s' % (request.path, request.META['QUERY_STRING'])
            return TemplateResponse(request, "android_post_auth.html", { 'app_link' : link }).render()
        else:
            return get_response(request)

    return middleware
