# Motion rules

Check each rule against the change. A row in the report names the rule it breaks.

**Duration bands**
- Button press: 100-160ms.
- Tooltip or popover: 125-200ms.
- Dropdown: 150-250ms.
- Modal or drawer: 200-500ms.
- Exits run shorter than entrances.
- Stagger runs 30-80ms per item and never blocks input.
- Once one tooltip is open, the next opens at once with no delay.
- Feedback to a press, key or hover starts at once; only the duration follows the band.

**Easing**
- Enter and exit use ease-out.
- Movement already on screen uses ease-in-out.
- Hover and colour changes use ease.
- Linear is only for constant motion such as a spinner.
- No ease-in anywhere, exits included.

**Interruptible and gesture-driven motion**
- It uses a spring that keeps its current velocity when retargeted. A fixed curve that restarts from zero is a mistake.
- Default bounce is 0. Bounce may reach about 0.3 and never passes 0.4.
- Bounce appears only at the end of a flick or in a deliberately playful tone, never on a plain click or tap.
- On the web that means the Web Animations API or a JS spring. CSS keyframes don't carry velocity.
- On release, project the endpoint from the velocity instead of snapping to the nearest point.
- Edges rubberband instead of stopping hard.

**Origin and space**
- Popovers scale from their trigger with `transform-origin`.
- Modals stay centred.
- Expanded content grows from its source element.
- Things leave the way they came.

**Feedback and hover**
- `:active` scales the control to about 0.97.
- Hover effects sit behind `@media (hover: hover) and (pointer: fine)`.

**Reduced motion and theme**
- Reduced motion keeps opacity and colour changes and drops movement. Crossfade instead of moving.
- A crossfade blur stays near 2px, never near 20px.
- The theme toggle switches instantly, with transitions suppressed during the switch.

**Frequency**
- An action used 100+ times a day gets no animation.
- An action used tens of times a day gets a minimal animation or none.
- Keyboard-initiated actions are never animated.

**Implementation**
- Name the transitioned properties. `transition: all` is a mistake.
- `will-change` appears only on elements that actually animate.

**How to check**
- Watch the motion at 2-5x slow motion in DevTools. Judge the origin, the easing and any overlap there, not at full speed.

Sources: https://emilkowal.ski/ui/great-animations, https://github.com/emilkowalski/skill, https://developer.apple.com/videos/play/wwdc2018/803/, https://developer.apple.com/videos/play/wwdc2023/10158/, https://www.joshwcomeau.com/animation/css-transitions/, https://paco.me/writing/disable-theme-transitions, https://rauno.me/craft/interaction-design
