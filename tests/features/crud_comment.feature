Feature: CRUD comment

    Scenario: Create from JSON post
        Given A few photos created
        When I send POST request with comment data in JSON format
        Then New comment is created
            And I receive a JSON response
            And Comment count is incremented by 1 in the commented photo
