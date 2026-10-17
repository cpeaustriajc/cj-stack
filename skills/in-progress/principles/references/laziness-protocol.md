# Laziness Protocol

**When:** you size a diff, or you want to add a layer, an abstraction or a flag that many
functions pass along.

**Rule:**

- Make each decision in one place. Pass its result to the other places as a plain value, such
  as one boolean.
- Make the smallest change that solves the problem. Fewer lines win over a pattern that looks
  better.

**You skipped it when:** the diff checks the same condition in two or more places, or a
parameter goes through functions that only pass it on.

**Not:** [Subtract Before You Add](subtract-before-you-add.md) removes old weight before the
new work. This principle keeps the new work small.
