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
        if hasattr(self, 'profile_url')
            return Profile.load(self.profile_url)
        else:
            return None


class Account(Resource):
    pass


class Application(Resource):

    def prepare_collections(self, *args, **kwargs):
        super(Application, self).prepare_collections(*args, **kwargs)

        self.accounts = Collection(
            url='/organizations/api/accounts/', type=Account, session=self._session
        )
        self.users = Collection(
            url='/accounts/api/create/', type=Identity, session=self._session
        )
