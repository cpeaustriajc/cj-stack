# Type System Discipline

**When:** you design types or a signature in a typed language.

**Rule:** Make the compiler reject impossible states, mixed-up primitives and unhandled
variants.

- Brand semantic primitives. `UserId` and `OrderId` are both strings, but they must not be
  interchangeable. Validate once when you create the value.
- External data has no type until a parse function turns it into the model. [Boundary
  Discipline](boundary-discipline.md) says where that function goes.
- Derive a type from the schema that owns the shape: OpenAPI, protobuf, GraphQL, a database
  migration or a token file. Do not write a parallel type by hand.
- Handle each variant exhaustively, so that a new variant is a compile error.

**You skipped it when:** a hand-written type copies a schema, two parameters of one primitive
type mean different things, or a cast replaces a parse on external data.

**Not:** [Model the Domain](model-the-domain.md) picks the structure. This principle makes the
compiler enforce it.
