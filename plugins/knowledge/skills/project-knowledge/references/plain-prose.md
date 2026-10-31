# Plain prose

Read this before you publish a page. `SKILL.md`, section "Writing safely", says when.

A check cannot match these, so read for them. Rewrite each one on a page before you publish it:

- **"Not only X but also Y", "not just X".** Say Y. "Not just a linter, it is a guard" becomes
  "It blocks the write."
- **Synonym cycling.** One name per thing. "the hook ... the guard ... the checker" becomes "the
  hook" each time.
- **Real names.** Use the name in the code. "the config loader" becomes `loadConfig`.
- **Abstract metaphor nouns** (surface, substrate, wedge, primitive, flywheel, north star). Name
  the thing. "the auth surface" becomes "the login and token endpoints".
- **Mannered prose** (aphorisms, code with feelings, "rides along"). "The cache quietly
  remembers" becomes "The cache keeps each result for 5 minutes."
- **Arrows and symbol-speak.** Write the sentence. "login → token → retry" becomes "After
  login, the client gets a token and retries once."
- **Dropped articles.** Keep "the" and "a" in sentences. "Fixes bug in parser" becomes "This
  fixes a bug in the parser."
- **"-ing" tails.** Split them off. "It adds a cache, ensuring fast reads" becomes "It adds a
  cache. Reads take 5 ms."
- **Feelings, not facts.** Give the measure. "This greatly improves search" becomes "Search
  takes 80 ms, not 900 ms." Test: could the sentence sit unchanged in another project's docs?
