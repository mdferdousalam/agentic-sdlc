# Profile: library

For published packages, SDKs and anything whose consumers are other developers.

## The public API is a promise

- Every exported symbol is intentional. A symbol exported by accident is a defect, not a
  feature, and removing it later is a breaking change.
- Every exported symbol has documentation that says what it does, what it returns, what it
  throws or rejects with, and one runnable example.
- A change to an exported signature, a default, an error type or a thrown condition is a
  breaking change, whatever the implementation looks like. The specification must say so.

## Versioning

- Semantic versioning, decided from the diff rather than from intent: removed or narrowed →
  major; added → minor; neither → patch.
- The changelog entry is written in the same commit as the change, in the consumer's language —
  what they must do, not what you refactored.
- Deprecate before removing: a release that warns, then a release that removes.

## Compatibility

- The supported runtime and dependency ranges are stated and tested, not assumed.
- No new required peer dependency in a minor release.
- Types ship with the package and are tested by compiling an example consumer.

## Tests

- Public behaviour is tested through the public entry point, not through internals.
- Every documented example is executed by a test; a broken README example is a bug.
