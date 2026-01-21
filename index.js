/**
 * Flubbable - A lightweight, chainable validation library for catching flubs before they happen
 * @module flubbable
 */

class Flub extends Error {
  constructor(message, field, value) {
    super(message);
    this.name = 'Flub';
    this.field = field;
    this.value = value;
  }
}

class Flubbable {
  constructor(value, fieldName = 'value') {
    this.value = value;
    this.fieldName = fieldName;
    this.errors = [];
  }

  /**
   * Check if value is not null or undefined
   */
  required(message) {
    if (this.value === null || this.value === undefined) {
      this.errors.push(message || `${this.fieldName} is required`);
    }
    return this;
  }

  /**
   * Check if value is a string
   */
  isString(message) {
    if (typeof this.value !== 'string') {
      this.errors.push(message || `${this.fieldName} must be a string`);
    }
    return this;
  }

  /**
   * Check if value is a number
   */
  isNumber(message) {
    if (typeof this.value !== 'number' || isNaN(this.value)) {
      this.errors.push(message || `${this.fieldName} must be a number`);
    }
    return this;
  }

  /**
   * Check if string has minimum length
   */
  minLength(min, message) {
    if (typeof this.value === 'string' && this.value.length < min) {
      this.errors.push(message || `${this.fieldName} must be at least ${min} characters`);
    }
    return this;
  }

  /**
   * Check if string has maximum length
   */
  maxLength(max, message) {
    if (typeof this.value === 'string' && this.value.length > max) {
      this.errors.push(message || `${this.fieldName} must be at most ${max} characters`);
    }
    return this;
  }

  /**
   * Check if number is within range
   */
  between(min, max, message) {
    if (typeof this.value === 'number' && (this.value < min || this.value > max)) {
      this.errors.push(message || `${this.fieldName} must be between ${min} and ${max}`);
    }
    return this;
  }

  /**
   * Check if value matches regex pattern
   */
  matches(pattern, message) {
    if (typeof this.value === 'string' && !pattern.test(this.value)) {
      this.errors.push(message || `${this.fieldName} has invalid format`);
    }
    return this;
  }

  /**
   * Check if value is a valid email
   */
  isEmail(message) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (typeof this.value === 'string' && !emailRegex.test(this.value)) {
      this.errors.push(message || `${this.fieldName} must be a valid email`);
    }
    return this;
  }

  /**
   * Check if value is in allowed list
   */
  oneOf(allowedValues, message) {
    if (!allowedValues.includes(this.value)) {
      this.errors.push(message || `${this.fieldName} must be one of: ${allowedValues.join(', ')}`);
    }
    return this;
  }

  /**
   * Custom validation function
   */
  custom(validatorFn, message) {
    try {
      const result = validatorFn(this.value);
      if (!result) {
        this.errors.push(message || `${this.fieldName} failed custom validation`);
      }
    } catch (err) {
      this.errors.push(message || `${this.fieldName} validation error: ${err.message}`);
    }
    return this;
  }

  /**
   * Check if there are any validation errors
   */
  hasFlubbed() {
    return this.errors.length > 0;
  }

  /**
   * Get all validation errors
   */
  getFlubs() {
    return this.errors;
  }

  /**
   * Throw if there are validation errors
   */
  orFlub(customMessage) {
    if (this.hasFlubbed()) {
      const message = customMessage || this.errors.join('; ');
      throw new Flub(message, this.fieldName, this.value);
    }
    return this.value;
  }

  /**
   * Get value if valid, otherwise return default
   */
  orDefault(defaultValue) {
    return this.hasFlubbed() ? defaultValue : this.value;
  }

  /**
   * Get value if valid, otherwise null
   */
  orNull() {
    return this.orDefault(null);
  }
}

/**
 * Create a new Flubbable validator
 */
function flubbable(value, fieldName) {
  return new Flubbable(value, fieldName);
}

/**
 * Validate an object with multiple fields
 */
function flubbableObject(obj, schema) {
  const errors = {};

  for (const [field, validator] of Object.entries(schema)) {
    const value = obj[field];
    const result = validator(new Flubbable(value, field));

    if (result.hasFlubbed()) {
      errors[field] = result.getFlubs();
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    orFlub: function(message) {
      if (!this.isValid) {
        const errorMessage = message || Object.entries(errors)
          .map(([field, errs]) => `${field}: ${errs.join(', ')}`)
          .join('; ');
        throw new Flub(errorMessage, 'object', obj);
      }
      return obj;
    }
  };
}

module.exports = {
  flubbable,
  flubbableObject,
  Flub
};
