Feature: Create photo

    Scenario: Create from enctype="multipart/form-data" HTML form
        Given A user created with username "mnopi" and password "1234"
            And A photo category created with name "smiling"
        When I go to "/test/photo" URL
            And I attach a file to photo form
            And I fill in "title" with "title bla bla bla"
            And I press the "ok" button
        Then New photo is created
            And Photo file is uploaded
            And I receive an JSON response

    Scenario: Create from JSON post
        Given A user created with username "mnopi" and password "1234"
            And A photo category created with name "smiling"
        When I send POST request with photo data in JSON format
        Then New photo is created
            And Photo file is uploaded
            And I receive an JSON response