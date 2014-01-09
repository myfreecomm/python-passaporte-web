# -*- coding: utf-8 -*-
import unittest

import requests
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, AccountMembers, AccountMember
from passaporte_web.tests.helpers import TEST_USER, TEST_USER_2, APP_CREDENTIALS

__all__ = ['AccountMembersTest']


class AccountMembersTest(unittest.TestCase):
     
    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

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

    def test_members_create_for_an_expired_account_fails(self):
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
