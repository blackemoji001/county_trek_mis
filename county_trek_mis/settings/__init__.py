import os
from dotenv import load_dotenv
load_dotenv()
env = os.getenv('DJANGO_SETTINGS_MODULE', 'county_trek_mis.settings.development')
if 'production' in env:
    from .production import *
else:
    from .development import *
