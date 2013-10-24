Feature: CRUD photo

    Scenario: Create from enctype="multipart/form-data" HTML form
        Given A user created with username "mnopi" and password "1234"
            And A photo category created with name "smiling"
        When I go to "/test/photo" URL
            And I attach a file to photo form
            And I fill in "title" with "title bla bla bla"
            And I press the "ok" button
        Then New photo is created with title "title bla bla bla"
            And Photo file is uploaded
            And Photo thumbnail file is uploaded with .p.png extension

    Scenario: Create from JSON post
        Given A user created with username "mnopi" and password "1234"
            And A photo category created with name "smiling"
        When I send POST request with photo data in JSON format
        Then New photo is created with title "prueba titulo android"
            And Photo file is uploaded
            And I receive a JSON response on client
            And The response status code is from "POST" request

    Scenario: Read photo list
        Given A few photos created
        When I send GET request on photo list URL
        Then I receive a JSON response on client
            And The response status code is from "GET" request

    Scenario: Read photo JSON
        Given A few photos created
        When I send GET request to read a concrete photo in JSON format
        Then I receive a JSON response on client
            And The response status code is from "GET" request
            And I can read the photo file referenced in the JSON object
