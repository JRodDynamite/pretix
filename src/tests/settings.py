from pretix.settings import *

TEST_DIR = os.path.dirname(__file__)

TEMPLATES[0]['DIRS'].append(os.path.join(TEST_DIR, 'templates'))