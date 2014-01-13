# -*- coding: utf-8 -*-
from httplib import urlsplit
from api_toolkit.entities import Collection, Resource, SessionFactory

__all__ = ['Notification', 'Profile', 'Identity', 'ServiceAccount', 'Application',]


class PWebSessionFactory(SessionFactory):

    @classmethod
    def get_auth(cls, **credentials):
        auth = super(PWebSessionFactory, cls).get_auth(**credentials)
        if auth == ('', ''):
            auth = (
                credentials.get('token', ''),
                credentials.get('secret', '')
            )
        return auth

    @classmethod
    def safe_kwargs(cls, **kwargs):
        kwargs = super(PWebSessionFactory, cls).safe_kwargs(**kwargs)
        for item in ('token', 'secret'):
            kwargs.pop(item, None)

        return kwargs


class PWebResource(Resource):
    session_factory = PWebSessionFactory

    @classmethod
    def load(cls, url, **kwargs):
        instance = super(PWebResource, cls).load(url, **kwargs)
        instance.load_options()
        return instance

    def update_meta(self, response):
        super(PWebResource, self).update_meta(response)
        content = response.json()
        if 'fields' in content:
            self._meta['fields'] = content['fields'].keys()
        else:
            self._meta['fields'] = self._meta.get('fields', None)


class PWebCollection(Collection):
    session_factory = PWebSessionFactory
    resource_class = PWebResource


class Notification(PWebResource):
    url_attribute_name = 'absolute_url'


class Notifications(PWebCollection):
    resource_class = Notification


class Profile(PWebResource):

    @property
    def url(self):
        if 'identity_info_url' in self.resource_data:
            return '{0.identity_info_url}/profile/'.format(self)
        
        return None


class Identity(PWebResource):
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
            resource_class=ServiceAccount, seed=self.resource_data.get('accounts', [])
        )

    def send_notification(self, body, **kwargs):
        kwargs.update({
            'body': body,
            'destination': self.uuid,
        })

        notifications = Notifications(
            url=self.resource_data['notifications']['list'], session=self._session
        )
        notification = notifications.create(**kwargs)

        return notification


class AccountMember(PWebResource):
    url_attribute_name = 'membership_details_url'
    
    def __init__(self, *args, **kwargs):
        super(AccountMember, self).__init__(*args, **kwargs)

        self._meta['fields'] = ['roles']

    @property
    def url(self):
        return super(AccountMember, self).url or self._response.url
    

class AccountMembers(PWebCollection):
    resource_class = AccountMember


class Account(object):
    # Accounts can only be manipulated via ServiceAccounts

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid

    @property
    def resource_data(self):
        return {'name': self.name, 'uuid': self.uuid}


class ServiceAccount(PWebResource):

    def __new__(cls, *args, **kwargs):
        instance_keys = kwargs.keys()
        if instance_keys == ['name', 'uuid']:
            instance = Account(**kwargs)
        elif instance_keys == ['account_data']:
            instance = Account(**kwargs['account_data'])
        else:
            instance =  PWebResource.__new__(cls, *args, **kwargs)

        return instance

    def __init__(self, *args, **kwargs):
        super(ServiceAccount, self).__init__(*args, **kwargs)

        self.account = Account(name=self.name, uuid=self.uuid)
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
            self.history = PWebCollection(url=self.history_url, session=self._session)

        if 'notifications_url' in self.resource_data:
            self.notifications = Notifications(url=self.notifications_url, session=self._session)

        if 'add_member_url' in self.resource_data:
            self.members = AccountMembers(url=self.add_member_url, session=self._session)

    def send_notification(self, body, **kwargs):
        kwargs['body'] = body
    
        return self.notifications.create(**kwargs)


class IdentityAccounts(PWebCollection):
    _seed = []

    def __init__(self, url, **kwargs):
        self._seed = kwargs.pop('seed', [])
        super(IdentityAccounts, self).__init__(url, **kwargs)

    def from_seed(self):
        for item in self._seed:
            account = ServiceAccount(**item)
            account._session = self._session
            yield account

    def get(self, *args, **kwargs):
        try:
            identity_account_url = self.url
            url_pieces = urlsplit(self.url)
            self.url = '{0.scheme}://{0.netloc}/organizations/api/accounts/'.format(url_pieces)
            return super(IdentityAccounts, self).get(*args, **kwargs)
        finally:
            self.url = identity_account_url


class ApplicationUsers(PWebCollection):

    def get(self, **kwargs):
        url_pieces = urlsplit(self.url)
        url = '{0.scheme}://{0.netloc}/accounts/api/identities/'.format(url_pieces)

        params = self.session_factory.safe_kwargs(**kwargs)
        params['session'] = self._session

        uuid = params.pop('uuid', None)
        if uuid:
            url = '{0}{1}/'.format(url, uuid)
        elif 'email' not in params:
            raise TypeError('Either "uuid" or "email" must be given')

        return self.resource_class.load(url, **params)

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


class Application(PWebResource):

    def __init__(self, host, token, secret):
        self.host = host
        self.token = token
        self.secret = secret
        super(Application, self).__init__()
        self.prepare_collections()

    def prepare_collections(self, *args, **kwargs):
        self.accounts = PWebCollection(
            url='{0}/organizations/api/accounts/'.format(self.host),
            token=self.token, secret=self.secret, resource_class=ServiceAccount
        )
        self.accounts.load_options()

        self.users = ApplicationUsers(
            url='{0}/accounts/api/create/'.format(self.host),
            token=self.token, secret=self.secret, resource_class=Identity
        )
        self.users.load_options()
