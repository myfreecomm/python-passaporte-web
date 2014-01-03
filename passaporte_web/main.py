# -*- coding: utf-8 -*-
from httplib import urlsplit
from api_toolkit import Collection, Resource

__all__ = ['Notification', 'Profile', 'Identity', 'Account', 'Application',]


class BaseResource(Resource):

    @classmethod
    def load(cls, url, **kwargs):
        instance = super(BaseResource, cls).load(url, **kwargs)
        instance.load_options()
        return instance

    def load_options(self):
        super(BaseResource, self).load_options()
        content = self.response.json()
        if 'fields' in content:
            self._meta['fields'] = content['fields'].keys()
        else:
            self._meta['fields'] = None


class Notification(BaseResource):
    pass


class Notifications(Collection):
    resource_class = Notification

    def __init__(self, *args, **kwargs):
        super(Notifications, self).__init__('/notifications/api/', *args, **kwargs)


class Profile(BaseResource):

    @property
    def url(self):
        if 'identity_info_url' in self.resource_data:
            return '{0.identity_info_url}/profile/'.format(self)
        
        return None


class Identity(BaseResource):
    url_attribute_name = 'update_info_url'

    @property
    def profile(self):
        if hasattr(self, 'profile_url'):
            return Profile.load(self.profile_url, session=self._session)
        else:
            return None


class Account(BaseResource):

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

        if self.expiration:
            # The api gives a datetime but expects a date
            self.expiration = self.expiration.split()[0]


class ApplicationUsers(Collection):
    resource_class = Identity

    def get(self, **kwargs):
        url_pieces = urlsplit(self.url)
        base_url = '{0.scheme}://{0.netloc}/accounts/api/identities/'.format(url_pieces)
        url_args = []

        if 'uuid' in kwargs:
            url = '{0}{1}/'.format(base_url, kwargs['uuid'])
        elif 'email' in kwargs:
            url = base_url
            url_args.append(('email', kwargs['email']))
        else:
            raise TypeError('Either "uuid" or "email" must be given')

        if 'include_expired_accounts' in kwargs:
            url_args.append(('include_expired_accounts', 'true'))
        if 'include_other_services' in kwargs:
            url_args.append(('include_other_services', 'true'))
            
        if url_args:
            qs_items = ['{0[0]}={0[1]}'.format(item) for item in url_args]
            url = '{0}?{1}'.format(url, '&'.join(qs_items))

        return self.resource_class.load(url, session=self._session)

    def authenticate(self, **kwargs):
        url_pieces = urlsplit(self.url)
        url = '{0.scheme}://{0.netloc}/accounts/api/auth/'.format(url_pieces)

        if 'email' in kwargs and 'password' in kwargs:
            user = self.resource_class.load(url, user=kwargs['email'], password=kwargs['password'])
        elif 'id_token' in kwargs:
            user = self.resource_class.load(url, password=kwargs['id_token'])
        else:
            raise TypeError('User credentials are required must be given')

        # The user credentials must not be used anymore
        del(user._session)
        user._session = self._session

        return user


class Application(BaseResource):

    def __init__(self, host, token, secret):
        self.host = host
        self.token = token
        self.secret = secret
        super(Application, self).__init__()
        self.prepare_collections()

    def prepare_collections(self, *args, **kwargs):
        self.accounts = Collection(
            url='{0}/organizations/api/accounts/'.format(self.host),
            user=self.token, password=self.secret, resource_class=Account
        )

        self.users = ApplicationUsers(
            url='{0}/accounts/api/create/'.format(self.host),
            user=self.token, password=self.secret, resource_class=Identity
        )
