# -*- coding: utf-8 -*-
# Django settings for complete pinax project.

import os.path
import posixpath
import pinax

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = 'default'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SERIALIZATION_MODULES = {
    'json': 'wadofstuff.django.serializers.json'
}

# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = DEBUG

ADMINS = (
     ('tor', 'tor@bash.no'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'dev.db'       # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

CACHE_MIDDLEWARE_KEY_PREFIX = 'turan'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        },
    'file': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        },
}

COMPRESS_CACHE_BACKEND = 'default'
COMPRESS_ROOT = os.path.join(PROJECT_ROOT, "site_media")
COMPRESS_ENABLED = True



# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Oslo'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'nn'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/'

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = '/static/'

# Additional directories which hold static files
STATICFILES_DIRS = (
    ('turan', os.path.join(PROJECT_ROOT, 'media')),
    ('bootstrap', os.path.join(PROJECT_ROOT, 'media', 'bootstrap')),
    ('silksprites', os.path.join(PROJECT_ROOT, 'media', 'silksprites')),
    ('flot', os.path.join(PROJECT_ROOT, 'media', 'flot')),
    ('openlayers', os.path.join(PROJECT_ROOT, 'media', 'openlayers')),
    ('jquery', os.path.join(PROJECT_ROOT, 'media', 'jquery')),
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
)

STATICFILES_EXTRA_MEDIA = (
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
    ('turan', os.path.join(PROJECT_ROOT, 'media')),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',

)
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(MEDIA_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%z3t0zu+99#5(m^w%-+q)m7tc2o9n#p_o%vah-$@7i_#))+0l8'

# List of callables that know how to import templates from various sources.

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openid.consumer.SessionConsumer',
    "pinax.apps.account.middleware.LocaleMiddleware",
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'turan.middleware.TuranSentryMarkup',
    'sentry.client.middleware.SentryResponseErrorIdMiddleware',
    'turan.middleware.TuranSentry404CatchMiddleware',
    'turan.middleware.Http403Middleware',
    'pinax.middleware.security.HideSensistiveFieldsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'turansite.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)


DEFAULT_FROM_EMAIL = 'turan@turan.no'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
#    "staticfiles.context_processors.static_url",
#    "social_auth.context_processors.facebook_api_key",

#"pinax.core.context_processors.contact_email",
#"pinax.core.context_processors.site_name",
    "pinax.core.context_processors.pinax_settings",

    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "pinax.apps.account.context_processors.account",
    #"account.context_processors.openid",
    #"account.context_processors.account",
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "turansite.context_processors.combined_inbox_count",

)

COMBINED_INBOX_COUNT_SOURCES = (
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "notification.context_processors.notification",
)

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.webdesign',
    'indexer',
    'paging',
    'sentry',
    'sentry.client',
    'pinax.templatetags',

#    'devserver',
    # external
    'notification', # must be first
    'django_openid',
    'emailconfirmation',
    'django_extensions',
    'robots',
    'friends',
    'mailer',
    'messages',
    'announcements',
    'oembed',
    #'djangodblog',
    'pagination',
#    'gravatar',
    'threadedcomments',
    'threadedcomments_extras',
#    'wiki',
#    'swaps',
    'timezones',
#    'app_plugins',
    'voting',
    'voting_extras',
    'tagging',
#    'bookmarks',
    'blog',
    'ajax_validation',
    'photologue',
    'avatar',
    'flag',
    'microblogging',
#    'locations',
    'uni_form',
    'django_sorting',
    'django_markup',

    'compressor',

# TUUURAN
    'turan',
    'piston',
    'api', # turan piston API
    'rosetta',
    'south',
    'debug_toolbar',
    
    # internal (for now)
    #
    #
    'social_auth',

    "pinax.apps.account",
    "pinax.apps.signup_codes",
    "pinax.apps.analytics",
    #"pinax.apps.profiles",
    #"pinax.apps.blog",
    #"pinax.apps.tribes",
    "pinax.apps.photos",
    "pinax.apps.topics",
    "pinax.apps.threadedcomments_extras",
  #  'analytics',
    'profiles',
    'django.contrib.staticfiles',
  #  'account',
#    'signup_codes',
    'pinax.apps.tribes',
    #'tribes',
   # 'photos',
    'tag_app',
   # 'topics',
    'groups',

#    'djkombu',
    'djcelery',
    'django.contrib.admin',
    'wakawaka',


    'groupcache',

# Alternative to fastcgi
#    'gunicorn',

)

GPX_STORAGE = '/home/turan.no/turansite/site_media/turan'
#DEFAULT_FILE_STORAGE = GPX_STORAGE



ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),
    ('creole', u'Creole'),
)
WIKI_MARKUP_CHOICES = MARKUP_CHOICES

AUTH_PROFILE_MODULE = 'profiles.Profile'
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_USER_DISPLAY = lambda user: user.get_profile().get_name()

AVATAR_DEFAULT_URL = MEDIA_URL + "turan/unknown.png"
AVATAR_GRAVATAR_BACKUP = True
AVATAR_GRAVATAR_DEFAULT = 'http://turan.no/site_media/turan/unknown.png'

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "turan@turan.no"
SERVER_EMAIL = CONTACT_EMAIL
SITE_NAME = "Turan"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "profile_redirect"
LOGIN_REDIRECT_URL = '/profiles/redirect/'

INTERNAL_IPS = (
    '10.2.4.100',
    '83.242.17.117',
)

LANGUAGES = (
    ('nn', 'Nynorsk'),
    ('no', u'Bokmål'),
    ('en', 'English'),
)

URCHIN_ID = "UA-7885298-3"

class NullStream(object):
    def write(*args, **kwargs):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'cloak_email_addresses': True,
    'file_insertion_enabled': False,
    'raw_enabled': False,
    'warning_stream': NullStream(),
    'strip_comments': True,
}


PAGINATION_INVALID_PAGE_RAISES_404 = True
SORTING_INVALID_FIELD_RAISES_404 = True
# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

WIKI_REQUIRES_LOGIN = True
WAKAWAKA_DEFAULT_INDEX = 'TuranFaq'


SENTRY_LOG_FILE = '/var/log/sentry.log'

# Uncomment this line after signing up for a Yahoo Maps API key at the
# following URL: https://developer.yahoo.com/wsregapp/
# YAHOO_MAPS_API_KEY = ''

import djcelery
djcelery.setup_loader()

BROKER_HOST = "localhost"
#BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
BROKER_PORT = 5672
BROKER_USER = "turan"
BROKER_PASSWORD = "tur4n"
BROKER_VHOST = "turan"
CELERYD_CONCURRENCY = 2
CELERYD_LOG_FILE = 'celeryd.log'
CELERY_RESULT_BACKEND = "amqp"
CELERY_ALWAYS_EAGER = False

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
#    'social_auth.backends.google.GoogleOAuthBackend',
#    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
#    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
#    'social_auth.backends.contrib.LiveJournalBackend',
#    'social_auth.backends.contrib.orkut.OrkutBackend',
#    'social_auth.backends.contrib.orkut.FoursquareBackend',
    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)
import random
SOCIAL_AUTH_DEFAULT_USERNAME = lambda: random.choice(['cipo', 'ilpirate', 'elefantino', 'pistelero', 'gruber'])


# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
