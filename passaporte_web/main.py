# -*- coding: utf-8 -*-
from httplib import urlsplit
from api_toolkit import Collection, Resource

__all__ = ['Notification', 'Profile', 'Identity', 'ServiceAccount', 'Application',]


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

    def prepare_collections(self, *args, **kwargs):
        url_pieces = urlsplit(self.url)
        user_accounts_url = '{0.scheme}://{0.netloc}/organizations/api/identities/{1.uuid}/accounts/'.format(url_pieces, self)
        self.accounts = IdentityAccounts(
            url=user_accounts_url, session=self._session,
            seed=self.resource_data.get('accounts', [])
        )


class Account(object):
    # Accounts can only be manipulated via ServiceAccounts

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid


class ServiceAccount(BaseResource):

    def __init__(self, *args, **kwargs):
        super(ServiceAccount, self).__init__(*args, **kwargs)

        if self.expiration:
            # The api gives a datetime but expects a date
            self.expiration = self.expiration.split()[0]

    @property
    def uuid(self):
        return self.get_account_attribute('uuid')

    @property
    def name(self):
        return self.get_account_attribute('name')

    def get_account_attribute(self, attrname):
        attrvalue = self.resource_data.get(attrname)
        if attrvalue is None and 'account_data' in self.resource_data:
            attrvalue = self.resource_data['account_data'].get(attrname)

        return attrvalue

    def prepare_collections(self, *args, **kwargs):
        if 'history_url' in self.resource_data:
            self.history = Collection(url=self.history_url, session=self._session)

        if 'notifications_url' in self.resource_data:
            self.notifications = Notifications(url=self.notifications_url, session=self._session)


class IdentityAccounts(Collection):
    resource_class = ServiceAccount
    _seed = []

    def __init__(self, url, **kwargs):
        self._seed = kwargs.pop('seed', [])
        super(IdentityAccounts, self).__init__(url, **kwargs)

    def from_seed(self):
        for item in self._seed:
            if 'url' in item:
                account = ServiceAccount(**item)
                account._session = self._session
            else:
                account = Account(**item)

            yield account


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

        # FIXME: Prepare collections must be called again in order to use the right credentials
        user.prepare_collections()

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
            user=self.token, password=self.secret, resource_class=ServiceAccount
        )
        self.accounts.load_options()

        self.users = ApplicationUsers(
            url='{0}/accounts/api/create/'.format(self.host),
            user=self.token, password=self.secret, resource_class=Identity
        )
        self.users.load_options()
