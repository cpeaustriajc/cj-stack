# Quality bar

Rules for any web app's designs, prototypes and screens. The project's own design system and
decision records win where they say more.

**Artboards and pages**
- One artboard is one page in one viewport and one state: `<Page> / <Viewport> / <State>`.
  Never two screens or two states in one artboard; an overlay, panel or sign-in step gets its own.
- Each page at 375, 768 and 1440 px, in light and dark if the app has both.
- Each state that applies: default, loading, empty, error, offline, signed out, signed in, long
  value, minimum data, hover, focus, pressed.
- An artboard at rest shows the finished state. Motion starts only on Play, never from a timer.
- A new screen is a proposal: put the current design beside option A and option B. A retired
  design moves to a Deprecated page marked "Do not build from these."
- Copy layout and measurements from the design 1:1. Never estimate from a picture of a board.

**Scope**
- Do the request at the smallest scope. Never redesign a part the request does not name, such as
  the shared header or footer.
- A treatment the design system does not describe is new: show it as an option first.

**Grid**
- One column grid with one gutter, and the same gap between rows. Vertical sizes are multiples
  of 8 px; 4 px steps only inside a component.
- A grid row has a fixed height; content does not set it. No masonry or dense packing.
- Measure alignment against the grid guides, never by eye.

**Layers**
- Content people return to or share gets a page with its own address, not an overlay.
- A layer shows feedback; a destination is a page.
- A scrim only behind a modal.

**States**
- Hover never carries information.
- Each state has two cues, such as an icon and text.

**Components**
- Use the project's kit components. Never draw a button, chip, card or menu by hand. A part the
  kit lacks goes into the kit first.
- Open each menu, select and popover on the board and check its items.
- A ported prototype keeps its behaviour exactly; changes are a separate option.

**Recording a design decision**

An approved decision gets a case study with these sections: summary; the problem with measured
values and the numbered requirements; the first attempt and why it failed; what the research
says (source, what it says, what it means for us); options and the decision; rejected options with
pictures; iteration (what was seen, the cause, the fix); the decision with its approval date,
numbered rules and a "Do not" list; what changed; open items; sources with the date opened.
Write the new rule into the design system in the same change. When a later decision replaces
part of it, add a dated "Superseded in part" banner and keep the old text.

**Definition of done**
1. Open each changed artboard or page in a browser; code and style strings are not enough.
2. Check light and dark at 375, 768 and 1440 px.
3. Turn on the grid guides and measure against columns and rows.
4. Measure each touch target: 44x44 or more.
5. Open each menu, select and popover.
6. Review accessibility: contrast, keyboard, focus ring, zoom, forced colours, reduced motion.
7. Hand over: what changed, which artboards, which rules applied, which treatments are new, and
   what was not checked.

**Known failures**
- Several screens or states in one artboard.
- A larger redesign than asked for.
- Hand-drawn components, or colours and materials the design system does not specify.
- "Done" reported before the board was opened; screenshots too small to show the grid guides.
- Boards empty at rest because they draw from timers.
- A prototype port that changed the design.
- A lesson left in a case study and not written into the design system.
- Heavy borders or edge rails; same-hue glow shadows under coloured buttons.
- A clipped glyph blamed on the font before anyone measured it.
