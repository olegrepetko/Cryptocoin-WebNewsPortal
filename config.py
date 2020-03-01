######## FLASK #######################
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]

######## MONGO #######################

MONGODB_SETTINGS = {'db': "cryptocoiners"}
RECAPTCHA_SITE_KEY = '-'
RECAPTCHA_SECRET_KEY = ''
RECAPTCHA_PUBLIC_KEY = '-'
RECAPTCHA_PRIVATE_KEY = ''
ONLINE_LAST_MINUTES = 5