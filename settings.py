from os import environ
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=0)
SESSION_CONFIGS = [
    dict(
        name='main',
        display_name="Main Experiment",
        num_demo_participants=3,
        app_sequence=['main'],  # Ensure your app is listed here
    ),
]
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = '$'
USE_POINTS = True
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = []
SESSION_FIELDS = []
ROOMS = [
    dict(
        name='invest_lab',
        display_name='Investment Experiment Lab'
    ),
]


ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
ALLOWED_HOSTS = ['inv-game.fly.dev']
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')


