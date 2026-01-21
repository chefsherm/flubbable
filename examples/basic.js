const { flubbable, flubbableObject, Flub } = require('../index.js');

console.log('=== Flubbable Examples ===\n');

// Example 1: Basic validation
console.log('1. Basic string validation:');
try {
  const email = flubbable('john@example.com', 'email')
    .required()
    .isEmail()
    .orFlub();
  console.log('   ✓ Valid email:', email);
} catch (err) {
  console.log('   ✗ Error:', err.message);
}

// Example 2: Validation with errors
console.log('\n2. Invalid email validation:');
try {
  const email = flubbable('not-an-email', 'email')
    .required()
    .isEmail()
    .orFlub();
  console.log('   ✓ Valid email:', email);
} catch (err) {
  console.log('   ✗ Error:', err.message);
}

// Example 3: Using defaults
console.log('\n3. Using default values:');
const port = flubbable('not-a-number', 'port')
  .isNumber()
  .orDefault(3000);
console.log('   Port value:', port);

// Example 4: Multiple validations
console.log('\n4. Multiple validation rules:');
const validator = flubbable('ab', 'username')
  .required()
  .isString()
  .minLength(3)
  .maxLength(20);

if (validator.hasFlubbed()) {
  console.log('   Validation errors:', validator.getFlubs());
} else {
  console.log('   ✓ Username is valid');
}

// Example 5: Number range validation
console.log('\n5. Number range validation:');
try {
  const age = flubbable(25, 'age')
    .required()
    .isNumber()
    .between(0, 120)
    .orFlub();
  console.log('   ✓ Valid age:', age);
} catch (err) {
  console.log('   ✗ Error:', err.message);
}

// Example 6: Enum validation
console.log('\n6. Enum validation:');
try {
  const status = flubbable('active', 'status')
    .oneOf(['active', 'inactive', 'pending'])
    .orFlub();
  console.log('   ✓ Valid status:', status);
} catch (err) {
  console.log('   ✗ Error:', err.message);
}

// Example 7: Custom validation
console.log('\n7. Custom validation:');
try {
  const username = flubbable('johndoe', 'username')
    .custom(v => !v.includes('admin'), 'Username cannot contain "admin"')
    .orFlub();
  console.log('   ✓ Valid username:', username);
} catch (err) {
  console.log('   ✗ Error:', err.message);
}

// Example 8: Object validation
console.log('\n8. Object validation:');
const user = {
  name: 'John Doe',
  email: 'john@example.com',
  age: 25,
  role: 'user'
};

const result = flubbableObject(user, {
  name: v => v.required().isString().minLength(2),
  email: v => v.required().isEmail(),
  age: v => v.required().isNumber().between(0, 120),
  role: v => v.oneOf(['user', 'admin', 'moderator'])
});

if (result.isValid) {
  console.log('   ✓ User object is valid');
} else {
  console.log('   ✗ Validation errors:', result.errors);
}

// Example 9: Object validation with errors
console.log('\n9. Object validation with errors:');
const invalidUser = {
  name: 'J',
  email: 'not-an-email',
  age: 150,
  role: 'superuser'
};

const invalidResult = flubbableObject(invalidUser, {
  name: v => v.required().isString().minLength(2),
  email: v => v.required().isEmail(),
  age: v => v.required().isNumber().between(0, 120),
  role: v => v.oneOf(['user', 'admin', 'moderator'])
});

if (invalidResult.isValid) {
  console.log('   ✓ User object is valid');
} else {
  console.log('   ✗ Validation errors:');
  for (const [field, errors] of Object.entries(invalidResult.errors)) {
    console.log(`      ${field}: ${errors.join(', ')}`);
  }
}

console.log('\n=== All examples completed ===');
