# flubbable

A lightweight, chainable validation library for catching flubs before they happen.

## What's a flub?

A flub is a mistake, error, or mishap. Flubbable helps you catch data validation flubs before they cause problems in your application.

## Installation

```bash
npm install flubbable
```

## Quick Start

```javascript
const { flubbable } = require('flubbable');

// Simple validation
flubbable('john@example.com', 'email')
  .required()
  .isEmail()
  .orFlub(); // Throws if validation fails

// With default values
const age = flubbable(null, 'age')
  .required()
  .isNumber()
  .orDefault(18); // Returns 18 if validation fails

// Check without throwing
const validator = flubbable('abc', 'username')
  .minLength(5)
  .maxLength(20);

if (validator.hasFlubbed()) {
  console.log(validator.getFlubs()); // ['username must be at least 5 characters']
}
```

## API Reference

### Basic Validation

#### `flubbable(value, fieldName)`

Creates a new validator for the given value.

```javascript
const validator = flubbable('test@example.com', 'email');
```

### Validation Methods

All methods are chainable and return the validator instance.

#### `.required(message?)`

Ensures the value is not null or undefined.

```javascript
flubbable(value, 'name').required().orFlub();
```

#### `.isString(message?)`

Validates that the value is a string.

```javascript
flubbable(value, 'name').isString().orFlub();
```

#### `.isNumber(message?)`

Validates that the value is a number.

```javascript
flubbable(value, 'age').isNumber().orFlub();
```

#### `.minLength(min, message?)`

For strings, validates minimum length.

```javascript
flubbable(value, 'password').minLength(8).orFlub();
```

#### `.maxLength(max, message?)`

For strings, validates maximum length.

```javascript
flubbable(value, 'username').maxLength(20).orFlub();
```

#### `.between(min, max, message?)`

For numbers, validates the value is within a range.

```javascript
flubbable(value, 'age').between(0, 120).orFlub();
```

#### `.matches(pattern, message?)`

Validates that a string matches a regex pattern.

```javascript
flubbable(value, 'zipcode').matches(/^\d{5}$/).orFlub();
```

#### `.isEmail(message?)`

Validates that the value is a valid email format.

```javascript
flubbable(value, 'email').isEmail().orFlub();
```

#### `.oneOf(allowedValues, message?)`

Validates that the value is in a list of allowed values.

```javascript
flubbable(value, 'status').oneOf(['active', 'inactive', 'pending']).orFlub();
```

#### `.custom(validatorFn, message?)`

Runs a custom validation function. The function should return true if valid.

```javascript
flubbable(value, 'username')
  .custom(v => !v.includes('admin'), 'Username cannot contain "admin"')
  .orFlub();
```

### Result Methods

#### `.hasFlubbed()`

Returns true if there are any validation errors.

```javascript
if (validator.hasFlubbed()) {
  console.log('Validation failed');
}
```

#### `.getFlubs()`

Returns an array of all validation error messages.

```javascript
const errors = validator.getFlubs();
console.log(errors); // ['field must be a string', 'field is required']
```

#### `.orFlub(customMessage?)`

Throws a Flub error if validation failed, otherwise returns the value.

```javascript
const validValue = flubbable(input, 'email').isEmail().orFlub();
```

#### `.orDefault(defaultValue)`

Returns the value if valid, otherwise returns the default value.

```javascript
const port = flubbable(process.env.PORT, 'port')
  .isNumber()
  .orDefault(3000);
```

#### `.orNull()`

Returns the value if valid, otherwise returns null.

```javascript
const optionalValue = flubbable(input, 'optional').isString().orNull();
```

### Object Validation

#### `flubbableObject(obj, schema)`

Validates multiple fields in an object.

```javascript
const { flubbableObject } = require('flubbable');

const user = {
  name: 'John',
  email: 'john@example.com',
  age: 25
};

const result = flubbableObject(user, {
  name: v => v.required().isString().minLength(2),
  email: v => v.required().isEmail(),
  age: v => v.required().isNumber().between(0, 120)
});

if (result.isValid) {
  console.log('User is valid!');
} else {
  console.log(result.errors);
}

// Or throw if invalid
result.orFlub();
```

## Error Handling

Flubbable provides a custom `Flub` error class:

```javascript
const { Flub } = require('flubbable');

try {
  flubbable('invalid-email', 'email').isEmail().orFlub();
} catch (err) {
  if (err instanceof Flub) {
    console.log(err.message); // 'email must be a valid email'
    console.log(err.field);   // 'email'
    console.log(err.value);   // 'invalid-email'
  }
}
```

## Examples

### User Registration

```javascript
const { flubbableObject } = require('flubbable');

function registerUser(data) {
  flubbableObject(data, {
    username: v => v.required().isString().minLength(3).maxLength(20),
    email: v => v.required().isEmail(),
    password: v => v.required().isString().minLength(8),
    age: v => v.required().isNumber().between(13, 120)
  }).orFlub('Invalid registration data');

  // If we get here, data is valid
  return createUser(data);
}
```

### API Input Validation

```javascript
const { flubbable } = require('flubbable');

app.post('/api/users', (req, res) => {
  try {
    const name = flubbable(req.body.name, 'name')
      .required()
      .isString()
      .minLength(2)
      .orFlub();

    const email = flubbable(req.body.email, 'email')
      .required()
      .isEmail()
      .orFlub();

    // Process valid data...
    res.json({ success: true });
  } catch (err) {
    if (err instanceof Flub) {
      res.status(400).json({ error: err.message });
    }
  }
});
```

### Configuration Validation

```javascript
const { flubbable } = require('flubbable');

const config = {
  port: flubbable(process.env.PORT, 'PORT')
    .isNumber()
    .between(1000, 65535)
    .orDefault(3000),

  host: flubbable(process.env.HOST, 'HOST')
    .isString()
    .orDefault('localhost'),

  env: flubbable(process.env.NODE_ENV, 'NODE_ENV')
    .oneOf(['development', 'production', 'test'])
    .orDefault('development')
};
```

## License

MIT