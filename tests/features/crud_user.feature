Feature: CRUD user

    Scenario: Create from JSON post
        When I send POST request with user data in JSON format
        Then New user is created
            And I receive a JSON response