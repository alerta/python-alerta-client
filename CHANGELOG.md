## v8.5.2 (2023-03-18)

### Refactor

- convert formatted strings to f-strings (#272)

## v8.5.1 (2021-11-21)

### Feat

- Add a --alert flag to alert keys to alert on expired and expiring key (#274)
- Add option to use custom value when creating API key (#270)

### Refactor

- convert formatted strings to f-strings (#272)
- assign api key directly (#271)

## v8.5.0 (2021-04-18)

### Fix

- improve alert note command (#263)
- consistent use of ID as metavar (#262)
- add scopes cmd and minor fixes (#257)
- **build**: run tests against correct branch

### Feat

- add examples for group cmd (#261)
- add and remove users to/from groups (#260)
- add option to list users to group cmd (#259)
- add option to list groups to user cmd (#258)
- add alerts command for list alert attributes (#256)
- show user details (#255)
- add option to show decoded auth token claims (#254)
- **auth**: add HMAC authentication as config option (#248)
