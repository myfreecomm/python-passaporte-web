# -*- coding: utf-8 -*-
from uuid import uuid4
import unittest

import requests
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, Notification
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['IdentityNotificationTest', 'ServiceAccountNotificationTest', 'NotificationTest']


class IdentityNotificationTest(unittest.TestCase):
    
    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

    def test_send_notification_returns_a_notification_destined_to_user(self):
        with use_pw_cassette('user/send_notification'):
            notification = self.user.send_notification('Notification de teste')
        
        self.assertTrue(isinstance(notification, Notification))
        self.assertEqual(notification.destination_data['uuid'], self.user.uuid)
        
    def test_send_notification_destination_cant_be_changed(self):
        test_uuid = str(uuid4())
        with use_pw_cassette('user/send_notification'):
            notification = self.user.send_notification(
                'Notification de teste', destination=test_uuid
            )
        
        self.assertTrue(isinstance(notification, Notification))
        self.assertNotEqual(notification.destination_data['uuid'], test_uuid)
        self.assertEqual(notification.destination_data['uuid'], self.user.uuid)

    def test_send_notification_should_accept_optional_params(self):
        test_url = 'http://example.com/' 
        test_tags = ['test', 'optional', 'params']
        test_schedule = '2142-01-01 00:00:00'

        with use_pw_cassette('user/send_notification'):
            notification = self.user.send_notification(
                'Notification de teste', scheduled_to=test_schedule,
                target_url=test_url, tags=test_tags,
            )

        self.assertTrue(isinstance(notification, Notification))
        self.assertEqual(notification.target_url, test_url)
        self.assertEqual(notification.scheduled_to, test_schedule)
        self.assertEqual(notification.tags, test_tags)


class ServiceAccountNotificationTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

        with use_pw_cassette('accounts/load_user_accounts'):
            self.service_account = self.user.accounts.from_seed().next()
            self.service_account.load_options()

    def test_send_notification_returns_a_notification_destined_to_the_service_account(self):
        with use_pw_cassette('accounts/send_notification'):
            notification = self.service_account.send_notification('Notification de teste')
        
        self.assertTrue(isinstance(notification, Notification))
        self.assertEqual(notification.destination_data['uuid'], self.service_account.uuid)
        
    def test_send_notification_should_accept_optional_params(self):
        test_url = 'http://example.com/' 
        test_tags = ['test', 'optional', 'params']
        test_schedule = '2142-01-01 00:00:00'

        with use_pw_cassette('accounts/send_notification'):
            notification = self.service_account.send_notification(
                'Notification de teste', scheduled_to=test_schedule,
                target_url=test_url, tags=test_tags,
            )

        self.assertTrue(isinstance(notification, Notification))
        self.assertEqual(notification.target_url, test_url)
        self.assertEqual(notification.scheduled_to, test_schedule)
        self.assertEqual(notification.tags, test_tags)

    def test_notifications_are_a_collection(self):
        with use_pw_cassette('accounts/notifications'):
            notifications = list(self.service_account.notifications.all())
        
        self.assertEquals(len(notifications), 5)
        self.assertTrue(isinstance(notifications[0], Notification))
    
    def test_notifications_should_be_ordered(self):
        with use_pw_cassette('accounts/notifications'):
            notifications = list(self.service_account.notifications.all())

        with use_pw_cassette('accounts/ordered_notifications'):
            ordered_notifications = list(self.service_account.notifications.all(ordering='newest-first'))

        notifications = sorted(notifications, key=lambda x: x.scheduled_to, reverse=True)
        
        self.assertEquals(len(ordered_notifications), 5)
        for i in xrange(5):
            self.assertEquals(notifications[i].resource_data, ordered_notifications[i].resource_data)


class NotificationTest(unittest.TestCase):
    
    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])
    
        with use_pw_cassette('user/send_notification'):
            self.notification = self.user.send_notification(
                'Notification de teste', scheduled_to='2142-01-01 00:00:00',
                target_url = 'http://example.com/', tags = ['test', 'optional', 'params']
            )
            self.notification.load_options()

    def test_should_delete_a_scheduled_notification(self):
        with use_pw_cassette('notification/delete'):
            self.notification.delete()
                
        with use_pw_cassette('notification/deleted_notification'):
            response = self.notification._session.get(self.notification.url)
            self.assertRaises(requests.HTTPError, response.raise_for_status)

    def test_should_only_delete_future_notifications(self):
        with use_pw_cassette('user/send_notification'):
            notification = self.user.send_notification('Notification de teste')
            notification.load_options()

        with use_pw_cassette('notification/delete_failure'):
            self.assertRaises(requests.HTTPError, notification.delete)
                
