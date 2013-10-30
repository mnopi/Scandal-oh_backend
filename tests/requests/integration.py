# # -*- coding: utf-8 -*-
#
# from tests.runner import SplinterTestCase
#
# class LoginTest(SplinterTestCase):
#     def tearDown(self):
#         self.browser.visit(self.live_server_url + logout_url)
#
#     def test_login_valid_user_by_username(self):
#         """
#         Scenario: Login valid user by username
#             Given a user with "<username>":"<password>"
#             When i log in with user "<username>":"<password>"
#             Then user is logged in
#                 And I receive a JSON response
#             Examples:
#                 |username|password|
#                 |paco33|123456|
#                 |miahon9992|123s3ewgsg|
#         """
#         staff = StaffFactory()
#         self.browser.visit(self.live_server_url + index_url)
#         self.browser.fill('username', staff.username)
#         self.browser.fill('password', '1234')
#         self.browser.find_by_css('#login .btn').click()
#         assert self.browser.path == index_url
#         assert login_url not in self.browser.url
#
#     def test_login_unregistered(self):
#         self.browser.visit(self.live_server_url + index_url)
#         self.browser.fill('username', 'margarito')
#         self.browser.fill('password', '1234')
#         self.browser.find_by_css('#login .btn').click()
#         assert login_url in self.browser.url
