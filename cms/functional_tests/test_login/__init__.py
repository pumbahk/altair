# -*- coding:utf-8 -*-
import unittest
try:
   from functional_tests import AppFunctionalTests, logout, login, get_registry, do_logout
   from functional_tests import delete_models, find_form
except ImportError:
   import sys
   import os
   sys.path.append(os.path.join(os.path.dirname(__name__), "../../"))
   from functional_tests import AppFunctionalTests, logout, login, get_registry, do_logout
   from functional_tests import delete_models, find_form

## here. test_login
class LoginLogoutFunctionalTests(AppFunctionalTests):
    """
    cms[login] ---- redirect ---> backend[login]
                                     |
    cms[after] <--- redirect ---- backend[login] OK
    """
    def test_login_redirect(self):
        app = self._getTarget()

        with logout(app):
            resp = app.get("/auth/login")
            self.assertEqual(resp.status_int, 200)

            login_resp = resp.click(linkid="login")
            self.assertEqual(login_resp.status_int, 302)

            client_id = get_registry().settings["altair.oauth.client_id"]
            login_resp.mustcontain(client_id)

    def test_after_backend_login_redirect(self):
        app = self._getTarget()
        with login(app):
            ## login後、loginしたorganization名が右上に表示される
            after_login_resp = app.get("/")
            after_login_resp.mustcontain("Administrator-this-is-login-name")        
            after_login_resp.mustcontain("demo-organization")

    def test_after_logout_redirect(self):
        app = self._getTarget()
        with login(app):
            do_logout(app)
            after_logout_resp = app.get("/")

            ### logout後はlogin情報見えない
            self.assertNotIn("Admoutistrator-this-is-login-name", after_logout_resp.ubody)
            self.assertNotIn("demo-organization",  after_logout_resp)


if __name__ == "__main__":
   unittest.main()
