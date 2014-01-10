# -*- coding: utf-8 -*-
import unittest

import requests
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, AccountMembers, AccountMember
from passaporte_web.tests.helpers import TEST_USER, TEST_USER_2, APP_CREDENTIALS

__all__ = ['AccountMembersTest', 'AccountMemberTest']


class AccountMembersTest(unittest.TestCase):
     
    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

        with use_pw_cassette('accounts/load_user_accounts'):
            self.service_account = self.user.accounts.all().next()
            self.service_account.load_options()

    def test_members_is_a_collection(self):
        self.assertTrue(isinstance(self.service_account.members, AccountMembers)) 

    def test_members_all_returns_a_list_of_account_member(self):
        with use_pw_cassette('accounts/members/list'):
            account_members = list(self.service_account.members.all())

        for i in account_members:
            self.assertTrue(isinstance(i, AccountMember))
   
    def test_members_create_with_user_role_returns_a_member_with_user_role(self):
        with use_pw_cassette('accounts/members/create_with_user_role'):
            account_member = self.service_account.members.create(
                identity=TEST_USER_2['uuid'], roles=['user']
            )

        self.assertTrue(isinstance(account_member, AccountMember))
        self.assertEquals(account_member.identity['uuid'], TEST_USER_2['uuid'])
        self.assertEquals(account_member.roles, ['user'])

    def test_members_create_with_owner_role_returns_a_member_with_owner_role(self):
        with use_pw_cassette('accounts/members/create_with_owner_role'):
            account_member = self.service_account.members.create(
                identity=TEST_USER_2['uuid'], roles=['owner']
            )

        self.assertTrue(isinstance(account_member, AccountMember))
        self.assertEquals(account_member.identity['uuid'], TEST_USER_2['uuid'])
        self.assertEquals(account_member.roles, ['owner'])

    def test_members_create_with_a_list_of_roles_returns_a_member_with_a_list_of_roles(self):
        with use_pw_cassette('accounts/members/create_with_list_of_roles'):
            account_member = self.service_account.members.create(
                identity=TEST_USER_2['uuid'], 
                roles=[unicode(range(5)), u'çãéê®©þ«»', u'test-user', u'668', u'user', u"{'a': 'a'}", u'owner', u'12345']
            )

        self.assertTrue(isinstance(account_member, AccountMember))
        self.assertEquals(account_member.identity['uuid'], TEST_USER_2['uuid'])
        self.assertEquals(
            account_member.roles, 
            [unicode(range(5)), u'çãéê®©þ«»', u'test-user', u'668', u'user', u"{'a': 'a'}", u'owner', u'12345'] 
        )

    def test_members_create_without_role_should_default_to_user_role(self):
        with use_pw_cassette('accounts/members/create_without_role'):
            account_member = self.service_account.members.create(
                identity=TEST_USER_2['uuid'], roles=[]
            )
        
        self.assertTrue(isinstance(account_member, AccountMember))
        self.assertEquals(account_member.identity['uuid'], TEST_USER_2['uuid'])
        self.assertEquals(account_member.roles, ['user'])

    def test_members_create_for_expired_account_fails(self):
        with use_pw_cassette('accounts/members/create_for_expired_account'):
            self.assertRaises(
                requests.HTTPError, self.service_account.members.create,
                identity=TEST_USER_2['uuid'], roles=[]
            )

    def test_create_with_inexistent_identity_fails(self):
        with use_pw_cassette('accounts/members/create_with_inexistent_identity'):
            self.assertRaises(
                requests.HTTPError, self.service_account.members.create,
                identity='00000000-0000-0000-0000-000000000000', roles=[]
            )

    def test_create_existent_account_member_fails(self):
        with use_pw_cassette('accounts/members/create_existent_account_member'):
            self.assertRaises(
                requests.HTTPError, self.service_account.members.create,
                identity=TEST_USER_2['uuid'], roles=[]
            )


class AccountMemberTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

        with use_pw_cassette('accounts/load_user_accounts'):
            self.service_account = self.user.accounts.all().next()
            self.service_account.load_options()

        with use_pw_cassette('accounts/members/list'):
            self.account_member = self.service_account.members.all().next()

    def test_load_should_keep_the_url_even_if_the_resource_data_doesnt_have_it(self):
        with use_pw_cassette('accounts/members/load_account_member_with_admin_role'):
            account_member = AccountMember.load(
                self.account_member.url, session=self.account_member._session
            )
    
        self.assertTrue(isinstance(account_member, AccountMember)) 
        self.assertEqual(self.account_member.url, account_member.url)
        self.assertFalse(account_member.resource_data.has_key(AccountMember.url_attribute_name))

    def test_successful_save_with_user_role(self):
        with use_pw_cassette('accounts/members/load_account_member_with_admin_role'):
            account_member = AccountMember.load(
                self.account_member.url, session=self.account_member._session
            )

        self.assertEquals(account_member.roles, ['admin'])

        with use_pw_cassette('accounts/members/update_with_user_role'):
            account_member.roles = ['user']
            account_member = account_member.save()

        self.assertEquals(account_member.roles, ['user'])

        with use_pw_cassette('accounts/members/load_account_member_with_user_role'):
            account_member = AccountMember.load(
                account_member.url, session=account_member._session
            )
        self.assertEquals(account_member.roles, ['user'])

    def test_successful_save_with_owner_role(self):
        with use_pw_cassette('accounts/members/load_account_member_with_admin_role'):
            account_member = AccountMember.load(
                self.account_member.url, session=self.account_member._session
            )

        self.assertEquals(account_member.roles, ['admin'])

        with use_pw_cassette('accounts/members/update_with_owner_role'):
            account_member.roles = ['owner']
            account_member = account_member.save()

        self.assertEquals(account_member.roles, ['owner'])

        with use_pw_cassette('accounts/members/load_account_member_with_owner_role'):
            account_member = AccountMember.load(
                account_member.url, session=account_member._session
            )
        self.assertEquals(account_member.roles, ['owner'])

    def test_successful_save_with_a_list_of_roles(self):
        with use_pw_cassette('accounts/members/load_account_member_with_admin_role'):
            account_member = AccountMember.load(
                self.account_member.url, session=self.account_member._session
            )

        self.assertEquals(account_member.roles, ['admin'])

        with use_pw_cassette('accounts/members/update_with_a_list_of_roles'):
            account_member.roles = [unicode(range(5)), u'çãéê®©þ«»', u'test-user', u'668', u'user', u"{'a': 'a'}", u'owner', u'12345'] 
            account_member = account_member.save()

        self.assertEquals(account_member.roles, [unicode(range(5)), u'çãéê®©þ«»', u'test-user', u'668', u'user', u"{'a': 'a'}", u'owner', u'12345'])

        with use_pw_cassette('accounts/members/load_account_member_with_a_list_of_roles'):
            account_member = AccountMember.load(
                account_member.url, session=account_member._session
            )

        self.assertEquals(account_member.roles, [unicode(range(5)), u'çãéê®©þ«»', u'test-user', u'668', u'user', u"{'a': 'a'}", u'owner', u'12345'])

    def test_successful_save_with_an_empty_list_of_roles_defaults_to_user_role(self):
        with use_pw_cassette('accounts/members/load_account_member_with_admin_role'):
            account_member = AccountMember.load(
                self.account_member.url, session=self.account_member._session
            )

        self.assertEquals(account_member.roles, ['admin'])

        with use_pw_cassette('accounts/members/update_with_empty_list_of_roles'):
            account_member.roles = []
            account_member = account_member.save()

        self.assertEquals(account_member.roles, ['user'])

        with use_pw_cassette('accounts/members/load_account_member_with_user_role'):
            account_member = AccountMember.load(
                account_member.url, session=account_member._session
            )
        self.assertEquals(account_member.roles, ['user'])

    def test_save_for_expired_account_fails(self):
        with use_pw_cassette('accounts/members/save_for_expired_account'):
            self.account_member.roles = ['user']
            self.assertRaises(requests.HTTPError, self.account_member.save)

    def test_succesful_delete(self):
        with use_pw_cassette('accounts/members/load_account_member_with_user_role'):
            account_member = AccountMember.load(
                self.account_member.url, session=self.account_member._session
            )

        with use_pw_cassette('accounts/members/delete'):
            account_member.delete()

        with use_pw_cassette('accounts/members/deleted_member'):
            self.assertRaises(
                requests.HTTPError, AccountMember.load,
                account_member.url, session=account_member._session
            )

    def test_delete_for_expired_account_fails(self):
        with use_pw_cassette('accounts/members/delete_for_expired_account'):
            self.assertRaises(requests.HTTPError, self.account_member.delete)
    
    def test_delete_for_owner_account_member_fails(self):
        with use_pw_cassette('accounts/members/load_account_member_with_owner_role'):
            account_member = AccountMember.load(
                self.account_member.url, session=self.account_member._session
            )

        with use_pw_cassette('accounts/members/delete_for_owner_account_member'):
            self.assertRaises(requests.HTTPError, account_member.delete)
            
