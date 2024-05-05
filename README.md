# GoITNeo CS HW-06

## Task

You need to implement the simplest web application without using a web framework.

### Instructions and requirements


Following the example in the course slides, create a web application with routing for two `html` pages: `index.html` and `message.html`.

#### Also:
 - handle static resources: `style.css`, `logo.png`;
 - organize work with form on page `message.html`;
 - in case of a `404 Not Found` error, return the `error.html` page;
 - your HTTP server should work on port `3000`.


#### For working with the form create a Socket server on port `5000`. The algorithm should be as follows:
 - enter data into the form;
 - they come into the web application, which then passes it further using `socket` (protocol `UDP` or `TCP` of your choice) to Socket server,
 - Socket server converts received byte-string into a dictionary and stores it in the MongoDB database.


#### Format of the MongoDB document to be as follows:
```json
{
    "date": "2022-10-29 20:20:58.020261",
    "username": "krabaton",
    "message": "First message"
},
{
    "date": "2022-10-29 20:21:11.812177",
    "username": "Krabat",
    "message": "Second message"
}
```

The key `"date"` of each message — is the time of receiving the message: `datetime.now()`. So each new message from web-app should write to the database with the time of receiving.

