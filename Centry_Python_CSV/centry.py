from centrySDK.centry import *
from csvInfoRetriever.config import *

CENTRY_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
CENTRY_SCOPE = 'public read_orders write_orders read_products write_products read_integration_config write_integration_config read_user write_user read_webhook write_webhook'

class CentrySdk:
    instance = None

    def __init__(self):
        self.instance = Centry(CENTRY_CLIENT_ID, CENTRY_SECRET, CENTRY_REDIRECT_URI)
        self.instance = self.instance.client_credentials(CENTRY_SCOPE)

    def sdk(self):
        if self.sdk is None:
            self.instance = Centry(CENTRY_CLIENT_ID, CENTRY_SECRET, CENTRY_REDIRECT_URI)
            self.instance = self.instance.client_credentials(CENTRY_SCOPE)
        return self.instance

