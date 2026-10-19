# Anatomy and proportion reference

Measurements for people, horses, dogs and cars, and the pose geometry that decided whether a pose read as natural. All values are in centimetres. Use them as defaults, and replace them with a canon or museum source when one exists.

## Contents
- Adult man, 180 cm
- Seated on the ground
- Pose geometry
- Horse
- Dog
- Cars
- Ratios to check at review

## Adult man, 180 cm

Heights from the floor, standing:

| Landmark | cm |
|---|---|
| Top of head | 180 |
| Ear canal (use it as the head's centre) | 166 |
| Chin | 157 |
| Base of neck (C7) | 154 |
| Shoulder joint centre (acromion about 3 cm higher) | 147 |
| Elbow | 112 |
| Hip joint | 92 |
| Wrist | 85 |
| Knee | 50 |
| Ankle | 8 |

Segment lengths and widths:

| Part | cm |
|---|---|
| Head, chin to crown / depth / width | 23 / 20 / 15.5 |
| Upper arm, shoulder to elbow | 33 |
| Forearm, elbow to wrist | 26 |
| Hand, wrist to middle fingertip / width at knuckles | 19 / 9 |
| Thigh, hip joint to knee | 44 |
| Shin, knee to ankle | 42 |
| Foot length / width | 26 / 10 |
| Shoulder breadth / shoulder joint centres | 40 / ±18.5 from the midline |
| Hip joints | ±9 from the midline, about 3.5 in front of the spine axis |
| Chest depth / waist width / hip width | 24 / 30 / 36 |
| Thigh / calf / upper arm diameter | 16 / 12 / 10 |

When a character has no canon height, use a named proxy (the actor's or mocap performer's height) and say so.

## Seated on the ground

- The hip joint sits about 9.5 above the seat.
- The shoulder joint is about 58-60 above the ground, and the top of the head about 92-95.
- With a shin vertical, the top of the knee is about 52 above the ground. That is only about 7 below the shoulder.
- A thigh raised 45° puts the knee centre about 31 above the hip joint and the shin slants forward. This is the comfortable "arm across the knee" height.
- Leaning against a trunk tilts the spine back 13-20° about the hips. That lowers the shoulders a little and moves the head back to touch the trunk.

## Pose geometry

- **Reach.** A hand target is reachable only if the distance from the shoulder is less than upper arm plus forearm (59). Solve the elbow with two-bone IK toward a pole direction: outward and down for an arm across a knee, outward and back for a hand resting on the thigh. Guessing the angles put Henry's arm horizontal, straining toward his knee.
- **Forearm across a raised knee.** The forearm lies about 9-10 above the knee centre once you count limb and armour radii. For the upper arm to angle down naturally, the knee top must sit at least 10-15 below the shoulder.
- **Sleeping head.** The head turns with the body (yaw within about 5° of the torso), the chin drops 10-15°, and the head lolls 15-20° toward one shoulder. Too little and he looks awake and strained. Too much and a helmet's lower edge sinks into the shoulder.
- **Resting weight.** Whatever carries weight shows it: a back flat against bark, shoulders slightly forward, arms limp with fingers curled about 30-45° per joint, never stretched straight.
- **Feet.** Planted feet have the ankle 8 above the ground and the sole flat. On an extended leg the heel rests on the ground and the foot falls outward 20-35°.
- **Foreshortening.** Turn the torso 45° toward the viewer and a raised thigh pointing at the camera projects at about 70% of its length. Get this from a 3D model rather than drawing it; that is why figures facing three-quarters are built in render3d.

## Horse (Pebbles, a 150 cm mare)

- Body length, point of shoulder to point of buttock, about equals the withers height. Drawn longer, the horse looks like a dachshund; the first Pebbles was 1.6× too long.
- The head is about 0.4 of the height (60).
- The legs are about half the height, from the ground to the elbow.
- The neck is about as long as the head.
- Grazing: the head hangs near vertical, the muzzle at grass level, and the poll below the withers.
- Hoof width is about 12. Give each hoof a ground shadow.

## Dog (Mutt, a medium dog with 52 cm withers)

- Body length is about 1.1 × the height at the withers.
- The head is about 22 long. The ears hang to about mid-cheek.
- Lying chin on paws: the forelegs point forward, the chest touches the ground, the haunches fold to one side, and the tail curves around.
- Small at page scale, so a face under about 25 px doesn't read. Say it with the silhouette and the coat pattern instead.

## Cars

A car in side view is judged as quickly as a face. A body on two circles, with the wheels hanging below a flat underside, no arches and no shadow, reads as a toy.
- A sports coupe (2013, Los Santos): 450 long, 130 tall, wheelbase 245, wheels 66 across. Front overhang about 95, rear about 110. Ground clearance about 12.
- A low wedge (2077, Night City): 470 long, 115 tall, wheelbase 270, wheels 72 across.
- Cut a wheel arch into the body about 1.2 × the wheel's radius, centred on the axle, and fill the gap behind the tyre with a dark wheel well. The tyre's top sits inside the arch, so the body's lower edge runs at about axle height between the wheels.
- Show the glass split by a B-pillar, a door line and a handle at belt height, a headlight and a taillight. Those five marks are what make a silhouette read as a car.
- A contact shadow under the car, about its own length and very flat, puts it on the road.
- Every car belongs to an era. A 2013 coupe painted dark is still a 2013 coupe in 2077. Draw the era's own car and swap them over the transition.

## Ratios to check at review

Measure on the picture, in pixels, against these:
- Helmet height ÷ seated height, ground to crown: about 0.35 with a bascinet, 0.25 bare-headed.
- Upper arm ÷ forearm: 1.27.
- Thigh ÷ shin: 1.05.
- Horse body length ÷ withers height: 1.0.
- Horse head ÷ withers height: 0.4.
- Dog body length ÷ withers height: 1.1.
- A sword's total length ÷ a standing man's height: about 0.65 for a longsword of 89 cm blade and about 120 cm total.
- Car length ÷ height: about 3.5 for a coupe, 4 for a wedge. Wheelbase ÷ length: about 0.55.
