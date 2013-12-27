# -*- coding: utf-8 -*-

from api_toolkit import Collection, Resource

__all__ = ['Notification', 'Identity', 'Account', 'Application',]


class Notification(Resource):
    pass


class Notifications(Collection):
    resource_class = Notification

    def __init__(self, *args, **kwargs):
        super(Notifications, self).__init__('/notifications/api/', *args, **kwargs)


class Identity(Resource):

    @property
    def profile(self):
        if hasattr(self, 'profile_url'):
            return Profile.load(self.profile_url)
        else:
            return None


class Account(Resource):
    pass


class Application(Resource):

    def __init__(self, host, token, secret):
        self.host = host
        self.token = token
        self.secret = secret
        super(Application, self).__init__({})
        self.prepare_collections()

    def prepare_collections(self, *args, **kwargs):
        self.accounts = Collection(
            url='{0}/organizations/api/accounts/'.format(self.host),
            user=self.token, password=self.secret, resource_class=Account
        )

        self.users = Collection(
            url='{0}/accounts/api/create/'.format(self.host),
            user=self.token, password=self.secret, resource_class=Identity
        )
