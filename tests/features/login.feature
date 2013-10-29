Feature: Login

    Scenario: Login valid user by username
        Given a user with "<username>":"<password>"
        When i log in with user "<username>":"<password>"
        Then user is logged in
            And I receive a JSON response
        Examples:
            |username|password|
            |paco33|123456|
            |miahon9992|123s3ewgsg|

    Scenario: Login vaild user by email
        Given a user with "<username>":"<password>":"<email>"
        When i log in with user "<email>":"<password>"
        Then user is logged in
            And I receive a JSON response
        Examples:
            |username|password|email|
            |paco33|123456|yo@yo.com|
            |miahon9992|123s3ewgsg|yo@exampleeee.com|

    Scenario: Logout user
        Given an user logged in
        When i send GET request to logout url
        Then user is logged out

#    Scenario:
#        Registro:
#            username(uq, max 15), email(uq, valid), password (min 6)
#
#        Login:
#            username | email
#            password

