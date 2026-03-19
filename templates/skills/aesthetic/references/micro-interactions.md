# Micro-Interactions

Use motion to strengthen comprehension and finish. Do not use motion to disguise weak structure.

## Duration ranges
- Hover and press feedback: 120-220ms
- Small UI transitions: 150-300ms
- Entry choreography: 200-500ms
- Larger scene changes: use sparingly and only when they help orientation

## Good motion choices
- Prefer opacity and transform over layout-thrashing properties.
- Use ease-out for entrance and ease-in for exit in most UI cases.
- Stagger only when it helps users parse sequence or hierarchy.
- Keep animations subtle on dense product surfaces.

## What to avoid
- constant looping motion with no informational value
- bounce or spring everywhere
- dramatic movement on every hover state
- long page-load sequences that delay interaction
- motion that ignores reduced-motion preferences

## Review checklist
- Does the motion explain state change or hierarchy?
- Would the screen still work with motion disabled?
- Is the timing consistent with the surface?
- Does the animation keep 60fps on a normal device?

If the answer is no, simplify the motion before polishing it.
