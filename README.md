[![pypi](https://img.shields.io/pypi/v/tom-registration.svg)](https://pypi.python.org/pypi/tom-registration)
[![run-tests](https://github.com/TOMToolkit/tom_registration/actions/workflows/run-tests.yml/badge.svg)](https://github.com/TOMToolkit/tom_registration/actions/workflows/run-tests.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/96d28f95266144f7afc7d118050b24ba)](https://www.codacy.com/gh/TOMToolkit/tom_registration/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=TOMToolkit/tom_registration&amp;utm_campaign=Badge_Grade)
[![Coverage Status](https://coveralls.io/repos/github/TOMToolkit/tom_registration/badge.svg?branch=main)](https://coveralls.io/github/TOMToolkit/tom_registration?branch=main)

# TOM Registration

This reusable TOM Toolkit app provides support for two user registration flows in the TOM Toolkit.

The two registration flows are as follows:

 1. Open Registration - In this flow, the user fills in a registration form and is immediately able to access the TOM as a member of the Public Group.

 2. Approval Registration - In this flow, the user fills in a registration form, and is inactive until an administrator reviews and approves their registration.

## Installation

 1. Install the package into your TOM environment:
   ```bash
   pip install bhtom_registration
   ```

 2. In your project `settings.py`, add `tom_registration` to your `INSTALLED_APPS` setting:

    ```python
    INSTALLED_APPS = [
        ...
        'bhtom_registration',
    ]
    ```

    And add the follow setting, with appropriate values for your use case:

    ```python
    TOM_REGISTRATION = {
        'REGISTRATION_AUTHENTICATION_BACKEND': 'django.contrib.auth.backends.ModelBackend',
        'REGISTRATION_REDIRECT_PATTERN': 'home',
        'SEND_APPROVAL_EMAILS': True
    }
    ```

    To prevent logged-in users from accessing the registration page, add `RedirectAuthenticatedUsersFromRegisterMiddleware` to the `MIDDLEWARE` settings:

    ```python
    MIDDLEWARE = [
        ...
        'bhtom_common.middleware.AuthStrategyMiddleware',
        'bhtom_registration.middleware.RedirectAuthenticatedUsersFromRegisterMiddleware',
    ]
    ```

 3. Depending on your preferred registration flow, include the appropriate tom_registration URLconf in your project `urls.py`. You will need to ensure that this urlpattern appears in the list before your `tom_common.urls`.

Open Registration:

    ```python
        urlpatterns = [
            ...
            path('', include('tom_registration.registration_flows.open.urls', namespace='registration')),
        ]
    ```

Approval Registration:

    ```python
        urlpatterns = [
            ...
            path('', include('tom_registration.registration_flows.approval_required.urls', namespace='registration')),
        ]
    ```

 4. While the registration views are now accessible directly, some changes need to be made to templates to make them available.

Copy the contents of [this file](https://github.com/TOMToolkit/tom_registration/blob/main/templates/tom_common/partials/navbar_login.html) to `templates/tom_common/partials/navbar_login.html`.

If you're using approval registration, copy the contents of [this file](https://github.com/TOMToolkit/tom_registration/blob/main/templates/auth/user_list.html) to `templates/auth/user_list.html`.

 5. If you're using approval registration and you would like a message informing the user that their account is pending approval if they try to log in prior to approval, you'll need to make the following changes:

First, in your `settings.py`, set the first item of your `AUTHENTICATION_BACKENDS`:

    ```python
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.AllowAllUsersModelBackend',
        'guardian.backends.ObjectPermissionBackend'
    )
    ```

Then, change the value of `REGISTRATION_AUTHENTICATION_BACKEND` in the `TOM_REGISTRATION` setting that was just created:

    ```python
    TOM_REGISTRATION = {
        'REGISTRATION_AUTHENTICATION_BACKEND': 'django.contrib.auth.backends.AllowAllUsersModelBackend`,
        ...
    }
    ```

## Email

In the approval required registration flow, there is available behavior to send basic emails notifying administrators of a registration request, and notifying users of registration approval. Administrators are determined by the [Django MANAGERS setting](https://docs.djangoproject.com/en/3.1/ref/settings/#managers). Email behavior can be enabled or disabled with `SEND_APPROVAL_EMAILS`.

The configuration of an email backend is a topic covered in depth by the [Django docs](http://docs.djangoproject.com/en/3.1/topics/email/#smtp-backend). There are a number of required settings that will need to be added.

In the future, `tom_registration` will provide more configurable behavior upon user registration/approval.

## Running the tests

In order to run the tests, run the following in your virtualenv:

`python manage.py test`
