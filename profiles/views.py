from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.newforms import form_for_model, form_for_instance
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, SiteProfileNotAvailable

from profiles.utils import get_profile_model


def create_profile(request, form_class=None, success_url=None,
                   template_name='profiles/create_profile.html'):
    """
    Create a profile for the user, if one doesn't already exist.
    
    To specify the form class used for profile creation, pass it as
    the keyword argument ``form_class``; if this is not supplied, it
    will fall back to ``form_for_model`` for the model specified in
    the ``AUTH_PROFILE_MODULE`` setting (and will raise
    ``SiteProfileNotAvailable`` if that setting is not specified or
    does not correspond to an installed model.
    
    If you are supplying your own form class, it must define a method
    named ``save()`` which corresponds to the signature of ``save()``
    on ``form_for_model``, because this view will call it with
    ``commit=False`` and then fill in the relationship to the user
    (which must be via a field on the profile model named ``user``, a
    requirement already imposed by ``User.get_profile()``) before
    finally saving the profile object. If many-to-many relations are
    involved, the convention established by ``form_for_model`` of
    looking for a ``save_m2m()`` method on the form is used, and so
    your form class should define this method.
    
    If the user already has a profile, as determined by
    ``request.user.get_profile()``, a redirect will be issued to the
    ``edit_profile()`` view.
    
    If no profile model has been specified in the
    ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.
    
    To specify a URL to redirect to after successful profile creation,
    pass it as the keyword argument ``success_url``; this will default
    to the URL of the ``profile_detail()`` view for the new profile if
    unspecified.
    
    To specify the template to use, pass it as the keyword argument
    ``template_name``; this will default to
    :template:`profiles/create_profile.html` if unspecified.
    
    Context:
    
        form
            The profile-creation form.
    
    Template:
    
        ``template_name`` keyword argument, or
        :template:`profiles/create_profile.html`.
    
    """
    try:
        profile_obj = request.user.get_profile()
        return HttpResponseRedirect(reverse('profiles_edit_profile'))
    except ObjectDoesNotExist:
        pass
    profile_model = get_profile_model()
    if success_url is None:
        success_url = reverse('profiles_profile_detail',
                              kwargs={ 'username': request.user.username })
    if form_class is None:
        form_class = form_for_model(profile_model)
        del form_class.base_fields['user']
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            profile_obj = form.save(commit=False)
            profile_obj.user = request.user
            profile_obj.save()
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=RequestContext(request))
create_profile = login_required(create_profile)

def get_initial_data(profile_obj):
    """
    Given a user profile object, returns a dictionary representing its
    fields, suitable for passing as the initial data of a form.
    
    """
    opts = profile_obj._meta
    data_dict = {}
    for f in opts.fields + opts.many_to_many:
        data_dict[f.name] = f.value_from_object(profile_obj)
    return data_dict

def edit_profile(request, form_class=None, success_url=None,
                 template_name='profiles/edit_profile.html'):
    """
    Edit a user's profile.
    
    To specify the form class used for profile editing, pass it as the
    keyword argument ``form_class``; this form class must have a
    ``save()`` method which will save updates to the profile
    object. If not supplied, this will default to
    ``form_for_instance`` for the user's existing profile object.
    
    If the user does not already have a profile (as determined by
    ``User.get_profile()``), a redirect will be issued to the
    ``create_profile()`` view; if no profile model has been specified
    in the ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.
    
    To specify the URL to redirect to following a successful edit,
    pass it as the keyword argument ``success_url``; this will default
    to the URL of the ``profile_detail()`` view if not supplied.
    
    To specify the template to use, pass it as the keyword argument
    ``template_name``; this will default to
    :template:`profiles/edit_profile.html` if not supplied.
    
    Context:
    
        form
            The form for editing the profile.
        
        profile
            The user's current profile.
    
    Template:
    
        ``template_name`` keyword argument or
        :template:`profiles/edit_profile.html`.
    
    """
    try:
        profile_obj = request.user.get_profile()
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('profiles_create_profile'))
    if success_url is None:
        success_url = reverse('profiles_profile_detail',
                              kwargs={ 'username': request.user.username })
    if form_class is None:
        form_class = form_for_instance(profile_obj)
        del form_class.base_fields['user']
    if request.method == 'POST':
        form = form_class(request.POST, initial=get_initial_data(profile_obj))
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return render_to_response(template_name,
                              { 'form': form,
                                'profile': profile_obj, },
                              context_instance=RequestContext(request))
edit_profile = login_required(edit_profile)

def profile_detail(request, username, template_name='profiles/profile_detail.html'):
    """
    Detail view of a user's profile.
    
    If no profile model has been specified in the
    ``AUTH_PROFILE_MODULE`` setting, or if the user has not yet
    created a profile, ``Http404`` will be raised.
    
    To specify the template to use, pass it as the keyword argument
    ``template_name``; this will default to
    :template:`profiles/profile_detail.html` if not supplied.
    
    Context:
    
        profile
            The user's profile.
    
    Template:
    
        ``template_name`` keyword argument or
        :template:`profiles/profile_detail.html`.
    
    """
    user = get_object_or_404(User, username=username)
    try:
        profile_obj = user.get_profile()
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response(template_name,
                              { 'profile': profile_obj },
                              context_instance=RequestContext(request))
