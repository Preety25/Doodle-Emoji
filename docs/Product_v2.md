# Doodle Emoji — Product Definition

**Status:** Build-first discovery / MVP planning  
**Working product name:** Doodle Emoji  
**Working concept:** Draw → Polish → Share  
**Platform strategy:** Cross-platform mobile first (iOS + Android)  
**Primary build stack:** React Native + Expo + TypeScript (initial recommendation)  
**Document purpose:** Living source of truth for product strategy, MVP scope, architecture principles, experiments, and decisions.

---

# 1. Product in one sentence

Doodle Emoji is a mobile app that lets people draw a quick, imperfect doodle and instantly turn it into a polished, expressive sticker or emoji-style visual that still feels recognizably like their original drawing, then save or share it through the apps they already use to communicate.

The initial product should optimize for one behavior:

> **I had a feeling or inside joke I wanted to express visually, so I drew something quickly, turned it into something delightful, and sent it to someone.**

---

# 2. Product thesis

Our current thesis is:

> People sometimes want a more personal visual reaction than generic emoji, GIFs, or existing stickers provide. A doodle-first creation flow can make personalized expression fast and low-effort because the user only needs to make a rough mark; the product does the hard work of making it polished and shareable.

The product is not fundamentally “an AI image generator.” The AI or 3D technology is an implementation mechanism.

The value proposition is:

> **Your doodle, but polished enough to send.**

The experience should feel closer to a tiny expressive toy than a design editor.

---

# 2A. Current direction after stylization research

**Updated:** 2026-09-22

The latest stylization research strengthens the central product hypothesis:

> **The highest-value capability is not generic sticker generation; it is transforming an imperfect user-authored doodle into something unexpectedly polished while preserving the feeling that the user made it.**

The current working moat hypothesis is:

**Faithful doodle preservation + distinctive stylization + delightful reveal.**

The transformation should improve dimensionality, material, lighting, polish, and presentation while being conservative about changing the user's silhouette, proportions, asymmetry, distinctive marks, and other quirks.

### Stylization Lab

Before locking the production transformation architecture, run a focused Stylization Lab that compares:

1. Procedural Blender rendering
2. AI image transformation
3. Hybrid procedural + AI enhancement

All three approaches should be tested against the same benchmark doodles and evaluated using the same rubric.

Initial hero styles:
- Gummy
- Clay
- Plush

The Lab is a technical and art-direction investigation, not a commitment that Blender or AI will be the final production implementation.

### Current technical hypothesis

A promising architecture is:

```text
User strokes
    ↓
Canonical doodle representation
    ↓
Shape-preserving transformation
    ↓
Procedural 3D foundation
    ↓
Versioned style recipe
    ↓
Hero render
    ↓
Optional AI enhancement
    ↓
Shareable asset
```

The original stroke representation is the canonical source asset. Rendered images are derived assets and must be reproducible from the source doodle plus transformation/style/version metadata.

### Blender role

Blender is currently being evaluated as a server-side/headless "hero renderer" and visual style laboratory.

The research indicates that a structured stroke representation can be converted into Blender curves, closed curves can be filled, open curves can be swept into geometry, geometry can be extruded/beveled/smoothed, procedural materials can be applied, and EEVEE can render transparent PNG output. Blender can also be automated through its Python API and command-line/background mode.

Blender should not be treated as the mobile UI or automatically assumed to be the final on-device 3D runtime. Its immediate purpose is to establish whether a controllable procedural transformation can achieve the desired visual quality.

### Product implication

The first technical question is not:

> "Which AI model should we use?"

It is:

> **"Can we create a transformation that makes people recognize their own doodle and immediately want to share it?"**

AI should be introduced where it adds capabilities that procedural transformation cannot provide reliably, such as semantic interpretation, richer characterization, camera-captured paper-doodle cleanup, backsides, or animation.

---

# 3. What the competitive research changed

The competitive research confirms that several parts of the original concept are already crowded:

- Generic custom sticker creation is established.
- Photo-to-sticker and selfie-to-sticker AI generation are crowded.
- Text-to-sticker / AI sticker generation is increasingly native to major communication platforms.
- Hand-drawn sticker creation already exists, including cross-messenger export.
- 3D emoji/sticker styling exists in adjacent AI products.
- Messenger-native sticker creation reduces the need for standalone utilities.

The important opportunity is therefore not:

> “We make custom stickers.”

It is more specifically:

> **“We make the fastest, most delightful way to turn an imperfect hand-drawn mark into a polished personal reaction.”**

The strongest differentiation hypothesis emerging from the research is:

### Doodle-first + faithful transformation + distinctive 3D visual language + very fast share loop

This differentiates from:

- photo-first AI sticker generators,
- selfie/avatar generators,
- text-prompt generators,
- traditional manual sticker editors,
- basic doodle-to-sticker apps,
- generic design tools.

The competitive research also suggests that the hardest and most valuable property is not “AI.” It is **preserving the user's authorship while adding polish**.

That means “accuracy to the original doodle” should be treated as a core product property.

---

# 4. Competitive landscape summary

## Major categories

### 1. General sticker platforms

Examples include Sticker.ly and other large sticker libraries.

Strengths:
- Massive discovery
- Existing social/network effects
- WhatsApp/Telegram workflows
- Large content libraries

Weaknesses / opportunity:
- Creation can feel secondary to browsing
- Ads/paywalls can add friction
- More about finding and remixing assets than expressing a spontaneous idea
- Doodle-first creation is not the center of the experience

### 2. Traditional doodle-to-sticker apps

Examples include Sticker Doodle, Sticker Doodle Machine, Draw an Emoji, and similar products.

Strengths:
- Very close to the core input behavior
- Simple and direct
- Some support multiple messengers
- Low conceptual complexity

Weaknesses / opportunity:
- Output is usually a direct doodle/sticker rather than a magical transformation
- Limited visual polish
- Limited personality or 3D treatment
- Limited AI-assisted interpretation
- Often feel like utilities rather than expressive consumer products

### 3. AI sticker/emoji generators

Examples include AI sticker makers, Genmoji alternatives, selfie-to-sticker products, and text-to-sticker apps.

Strengths:
- High novelty
- Strong visual output
- Multiple styles
- AI-driven variation
- Pack generation

Weaknesses / opportunity:
- Input is often a selfie, photo, or text prompt
- Less authorship and less connection to the user's original mark
- Output can be unpredictable
- Generation introduces latency/cost
- Many look interchangeable

### 4. Native messenger creation

WhatsApp, Apple Messages, Telegram, Discord, Slack and other platforms now cover portions of sticker/emoji creation or distribution.

Strength:
- Very short path from creation to communication

Weakness:
- Platform-specific
- Limited creative identity
- Limited cross-messenger ownership
- Less opportunity to establish an independent visual language

### 5. Avatar / identity products

Bitmoji and avatar-style products prove that people will use personal visual representations repeatedly.

Strength:
- Strong identity
- Large libraries of expressions
- High repeat potential

Weakness:
- Identity is usually built through menus/parts rather than spontaneous drawing
- Higher setup effort
- More like “build your avatar” than “express this moment”

---

# 5. Product opportunity

The current opportunity hypothesis is a white-space intersection:

```text
Fast like an emoji
        +
Personal like a doodle
        +
Polished like an illustration
        +
Expressive like a sticker
        +
Ownable like a personal character
        +
Shareable like a messaging asset
```

The product should not ask the user to become a designer.

The user's job is simply:

> **Make a mark.**

The app should do the rest.

---

# 6. Target users — initial hypotheses

We will start with behavioral segments rather than demographic personas.

## Primary hypothesis: expressive chatters

People who frequently use:

- emoji
- stickers
- GIFs
- memes
- reaction images
- visual messages

They already communicate visually and understand the value of expressive assets.

Potential unmet need:

> “The exact reaction I want does not exist.”

## Secondary hypothesis: inside-joke communicators

Close friends, couples, siblings, group chats, and communities.

Potential unmet need:

> “I want something that only makes sense to us.”

This segment is strategically interesting because it could eventually create a shared visual language.

## Secondary hypothesis: casual creatives

People who doodle, sketch, journal, decorate, or enjoy making small visual objects.

Potential unmet need:

> “I enjoy making things, but I do not want to spend time making them polished.”

## Secondary hypothesis: reaction creators

People who frequently make/share reaction images, memes, stickers, or custom social assets.

Potential unmet need:

> “I want the perfect reaction faster.”

These segments are hypotheses. We will eventually validate where the strongest repeat behavior exists.

---

# 7. Jobs to be done

The strongest current JTBD hypotheses are:

### Functional job

> When I want to express a specific feeling, joke, reaction, or inside reference, I want to make a personal visual quickly so I can communicate exactly what I mean.

### Emotional job

> I want the thing I send to feel like it came from me, not from a generic sticker library.

### Social job

> I want to create something that makes the other person feel like “this is ours.”

---

# 8. Core experience principle

The core loop should be:

```text
OPEN
  ↓
DRAW
  ↓
POLISH
  ↓
REVEAL
  ↓
SAVE / SHARE
  ↓
DRAW AGAIN
```

The product should aim for a short path from launch to first result.

Working first-target:

> **Under 90 seconds from first launch to first polished/shareable creation.**

For repeat users, the aspiration is much shorter:

> **A few seconds from idea to creation start, then a very short transformation/reveal.**

The exact target should be validated rather than treated as a permanent requirement.

---

# 9. MVP product promise

The MVP should make one promise extremely well:

> **Draw something messy. We will make it look good without making it stop feeling like yours.**

This implies that the transformation must preserve:

- silhouette
- basic proportions
- gesture
- distinctive marks
- the “personality” of the original drawing

The transformation should add:

- dimension
- lighting
- depth
- material
- polish
- clean transparency
- presentation quality

---

# 10. MVP scope

## Core MVP journey

```text
Launch
  ↓
New doodle
  ↓
Draw
  ↓
Polish
  ↓
Reveal
  ↓
Result
  ↓
Save
  ↓
Share
```

## MVP screens

### Home

Purpose:
- Start a new creation
- Access recent creations

Minimum content:
- Primary “Draw” action
- Recent creations

### Draw

Required:
- finger/stylus drawing
- undo
- redo
- clear
- basic color
- basic stroke size
- transparent canvas
- save original stroke data

Avoid turning this into a full drawing editor.

### Transform

The user chooses one obvious primary action:

> Make it 3D

or

> Polish

The transformation should feel like a reveal, not a progress bar.

### Result

Required:
- large visual preview
- save
- share
- remix/retry
- regenerate if applicable

### Library

Required:
- recent creations
- tap to view
- delete

### Share

Use the operating system's native sharing mechanism first rather than building direct integrations for each messaging platform.

---

# 11. What is NOT in MVP

Do not build these initially:

- social feed
- public profiles
- followers
- likes
- comments
- messaging
- contact syncing
- community marketplace
- creator marketplace
- public discovery feed
- complex animation editor
- advanced drawing layers
- advanced vector editing
- full sticker-pack marketplace
- subscription system
- elaborate onboarding
- native iMessage extension
- native Android sticker-pack system
- multi-user collaboration

These can become future opportunities once the core behavior is validated.

---

# 12. MVP transformation strategy

The product should separate the concept of a "doodle" from the implementation used to transform it.

The app should treat a doodle as a structured source asset rather than only a final PNG.

For example:

```text
Doodle
 ├── stroke data
 ├── canvas size
 ├── colors
 ├── stroke widths
 └── metadata
```

This allows us to re-render a creation later using different transformation engines.

This is a key long-term architectural requirement.

---

# 12A. Asset and export strategy

A **1024×1024 RGBA PNG is a master/hero asset, not a universal final sticker format**.

For normal image sharing through the operating system's share sheet, a high-resolution transparent master is useful, but receiving apps may resize, recompress, or impose their own rules.

For native sticker workflows, generate platform-specific derivatives from the canonical master.

Current official platform constraints to design around:

- **WhatsApp static stickers:** 512×512 pixels and no more than 100 KB. Animated stickers: 512×512 and no more than 500 KB, with additional animation constraints.
- **Telegram static stickers:** PNG or WebP; one dimension must be exactly 512 pixels; transparency is supported. Telegram's current import documentation permits static stickers up to 512 KB.
- **Apple Messages stickers:** choose one sticker size for a pack and provide @3x assets at 300×300, 408×408, or 618×618 pixels; files must be 500 KB or smaller.

Therefore the rendering/export pipeline should be:

```text
Canonical creation
       ↓
High-quality master
1024×1024 RGBA PNG
       ↓
Export service
       ├── General share asset
       ├── WhatsApp 512×512 WebP
       ├── Telegram 512×512 PNG/WebP
       └── iMessage 300/408/618 @3x PNG/APNG
```

The master should be retained even when the user shares a derivative.

Every derived asset should reference:
- creation ID
- export target
- export dimensions
- file format
- compression setting
- transformation version
- style version

The 1024px master should be tested at 512px, 256px, and approximately 128px to ensure that the style still reads when reduced.

**Primary implementation rule:** do not treat 1024px PNG as the single "sticker format." Treat it as the canonical high-quality source from which destination-specific assets are derived.

**Current official references (checked 2026-09-22):**
- WhatsApp Help Center: https://faq.whatsapp.com/1056840314992666
- Apple Human Interface Guidelines — iMessage apps and stickers: https://developer.apple.com/design/human-interface-guidelines/imessage-apps-and-stickers
- Apple Messages sticker pack requirements: https://developer.apple.com/documentation/messages/adding-your-sticker-packs-to-messages
- Telegram stickers: https://core.telegram.org/api/stickers
- Telegram sticker import requirements: https://core.telegram.org/import-stickers

---

# 13. Transformation engine architecture

Create an abstract transformation layer.

Conceptually:

```text
Doodle
   ↓
TransformationService
   ├── Local3DEngine
   ├── AIEngine
   ├── FutureEngine
   └── AnimationEngine
```

The UI should not directly know which provider or algorithm produced the result.

This will let us change the transformation technology later without rebuilding the rest of the app.

---

# 14. Transformation roadmap

## V0 / technical prototype

Try to make a compelling result with deterministic/procedural processing.

Goal:

> Can a rough shape become a beautiful 3D object without AI?

Possible steps:

```text
Stroke capture
→ silhouette
→ contour cleanup
→ depth/extrusion
→ bevel
→ material
→ lighting
→ soft shadow
→ transparent asset
```

Advantages:
- fast
- deterministic
- low marginal cost
- no network requirement
- consistent visual language

## V1

Add AI remix as an optional second path.

Example:

```text
Original doodle
   ├── Make 3D
   └── Remix
         ├── Gummy
         ├── Clay
         ├── Plush
         ├── Glossy
         └── Surprise Me
```

The default experience should not depend on AI unless research proves that AI output provides substantially more user value.

---

# 15. Why "faithful polish" matters

The competitor research reveals a useful distinction.

Many AI products optimize for:

> “Generate something good from my input.”

Our product should optimize for:

> **“Make my thing better without replacing it.”**

That is a different product promise.

A successful result should cause a user to think:

> “OMG, that's the exact thing I drew.”

rather than:

> “That's a cool image.”

Both are good, but the first is much more ownable.

---

# 16. Signature visual direction

The MVP should establish a recognizable visual language.

Initial hypothesis:

- soft 3D form
- slightly inflated / rounded surfaces
- expressive lighting
- subtle gloss or material response
- clean transparent background
- tasteful shadow
- recognizable silhouette
- playful but not childish
- visually consistent across creations

The exact material and style system should be explored through visual prototypes.

Possible styles later:

- Gummy
- Clay
- Plush
- Jelly
- Glossy
- Paper
- Chrome
- Candy
- Soft toy
- Glow
- Pixel
- Hand-painted

The style system should be data-driven rather than hard-coded into individual screens.

---

# 17. Product differentiation hypotheses

We should test these, not assume them:

### D1 — Doodle-first

Starting with a user's own mark is more personal than starting with a prompt or selfie.

### D2 — Faithful transformation

Preserving the original doodle creates more emotional ownership than generic generation.

### D3 — Fast transformation

The user should not need to learn editing tools or write prompts.

### D4 — Distinctive 3D polish

A consistent 3D visual language makes the output feel more valuable/shareable.

### D5 — Cross-messenger ownership

The creation should belong to the user rather than to a single messaging platform.

### D6 — Personal visual language

Repeated use may allow users to build a recognizable library of their own expressions.

---

# 18. Future product vision

The long-term vision is larger than "sticker maker."

Potential evolution:

```text
Doodle
   ↓
Polished sticker
   ↓
Reaction library
   ↓
Personal visual language
   ↓
Characters / recurring motifs
   ↓
Animated reactions
   ↓
Shared friend/group visual language
   ↓
Creator styles / packs
```

Long-term product vision hypothesis:

> **A personal visual language for digital conversation.**

This is intentionally a north-star direction, not an MVP commitment.

---

# 19. Core product metrics

We will not optimize around downloads alone.

## Activation

- app_opened
- drawing_started
- first_creation_completed

Primary activation candidate:

> % of new users who complete one creation

## Creation

- drawing_started
- drawing_completed
- transformation_started
- transformation_completed
- transformation_failed

## Value

- result_viewed
- result_saved
- share_sheet_opened

Potential primary value metric:

> % of completed creations that trigger a share action

## Retention

- second_creation
- day-1 creator retention
- day-7 creator retention
- day-30 creator retention

## Quality

- generation latency
- transformation success rate
- crash-free sessions
- user-reported similarity / satisfaction

---

# 20. North Star metric — working hypothesis

Initial candidate:

> **Weekly active users who create and initiate sharing of at least one personalized visual.**

Why:

The real product value is not image generation.

It is expression that results in communication.

This metric should be revisited after beta evidence.

---

# 21. Business model hypotheses

Do not commit to a monetization model before we understand repeat behavior.

Possible models:

### Free core + premium styles

Free:
- core transformations
- basic library
- share

Paid:
- premium materials/styles
- advanced transformations
- animation

### AI generation credits

Useful if AI generation has meaningful variable cost.

### Subscription

Potentially appropriate later if the service includes recurring value such as:
- continuously expanding styles
- cloud library
- animation
- premium transformation engines
- new creative tools

### One-time packs

Potentially useful for:
- style packs
- animated packs
- special transformation sets

### Creator ecosystem

Long-term possibility, not MVP.

---

# 22. Business model principle

Do not ask:

> "How can we monetize this?"

Ask:

> **"What recurring value would make a user willingly pay?"**

The monetization model should follow the usage pattern.

---

# 23. Risks

## Product risk

The idea may be fun once but not habitual.

Validation:
- repeated-creation testing
- beta retention

## Differentiation risk

The product may feel like another sticker generator.

Validation:
- competitive research
- concept testing
- positioning tests

## Transformation-quality risk

AI or procedural transformation may not preserve the user's doodle.

Validation:
- technical spike
- visual test set
- user similarity rating

## Latency risk

Generation may take too long.

Validation:
- prototype timing
- technical benchmarks

## Cost risk

AI generation may become too expensive at scale.

Validation:
- cost per generation
- caching
- local default path

## Platform risk

Messaging platforms may change capabilities.

Mitigation:
- use native OS sharing first
- keep messenger-specific features modular

## Content / safety risk

AI-generated content may produce unwanted or inappropriate results.

Mitigation:
- explicit input/output handling
- provider moderation capabilities
- reporting and filtering strategy
- style constraints

## Privacy risk

Drawings may be uploaded to remote services.

Mitigation:
- local default transformation
- explicit AI opt-in
- clear retention policy
- minimal data collection

## Build-complexity risk

The project can easily expand into a full editor/social network.

Mitigation:
- strict MVP scope
- assumption-driven roadmap
- decision log

---

# 24. Technical principles

### Principle 1 — Keep the core creation model stable

The canonical user asset is the doodle/stroke representation.

### Principle 2 — Isolate transformation engines

Never hard-code the UI around one AI provider.

### Principle 3 — Keep sharing independent

Treat sharing as an output capability rather than a feature owned by a specific messenger.

### Principle 4 — Preserve source data

Keep the original doodle so it can be transformed again in future styles.

### Principle 5 — Make styles configurable

Style definitions should be data-driven.

### Principle 6 — Keep AI optional

The app should have a useful non-AI baseline unless research proves otherwise.

### Principle 7 — Measure from the beginning

Analytics should be designed into the product before beta.

---

# 25. Recommended initial technology strategy

## Mobile

React Native + Expo + TypeScript

Why:
- cross-platform first
- good fit for the current development environment
- rapid iteration
- one shared application
- can later add native capabilities where necessary

## Navigation

Expo Router

## Drawing

Select a well-supported React Native drawing/canvas approach after a feasibility spike. The requirement is low-latency freehand interaction and export of both stroke data and rendered output.

## Backend

Keep minimal initially.

Potential responsibilities:
- AI gateway
- generation jobs
- asset handling
- analytics events that cannot be generated entirely client-side
- later authentication/cloud library

Do not commit to a complex backend architecture before the generation workflow is proven.

## AI

Integrate behind our own transformation interface.

Never expose provider API keys in the mobile client.

## Storage

Local-first for MVP.

Cloud storage can be added when sync/accounts become necessary.

## Sharing

Use native iOS/Android sharing first.

Messenger-specific sticker integrations are a later layer.

---

# 26. Repository structure

Recommended initial structure:

```text
doodle-emoji/
│
├── PRODUCT.md
├── ASSUMPTIONS.md
├── RESEARCH-PLAN.md
├── COMPETITIVE-LANDSCAPE.md
├── BUSINESS-MODEL.md
├── RISKS.md
├── METRICS.md
├── ROADMAP.md
├── DECISIONS.md
│
├── research/
├── design/
│
└── app/
```

As engineering grows:

```text
app/
├── app/
├── components/
├── features/
│   ├── drawing/
│   ├── transformation/
│   ├── library/
│   ├── sharing/
│   └── analytics/
├── services/
│   ├── transformation/
│   ├── storage/
│   └── analytics/
├── models/
├── assets/
└── config/
```

Folder names are guidelines, not a rigid contract.

---

# 27. AI collaboration model

## ChatGPT

Use for:
- strategy
- product framing
- research plans
- interview guides
- synthesis
- hypothesis management
- UX reasoning
- experiment design
- business model thinking
- roadmap decisions
- architecture review
- PRDs

## Grok Bot — Research

Use for:
- current competitor investigation
- app-store research
- web research
- Reddit/community research
- platform documentation
- market scanning

## Grok Bot — Architect

Use for:
- technical feasibility
- platform capabilities
- rendering approaches
- performance questions
- API architecture
- technical spikes
- dependency research

## Grok Bot — QA

Use for:
- exploratory testing
- edge cases
- accessibility review
- UX issues
- browser/device testing
- bug investigation

## Cursor

Use for:
- project setup
- implementation
- debugging
- refactoring
- running tests
- local development
- Git/versioning

---

# 28. AI handoff rule

Every AI task should contain:

1. Context
2. Question
3. Evidence
4. Unknowns
5. Constraints
6. Task
7. Expected deliverable
8. Stop condition

The AI should not make irreversible product decisions without review.

---

# 29. Product decision log

Record consequential decisions in DECISIONS.md.

Template:

```text
# Decision

Date:

Decision:

Context:

Evidence:

Alternatives considered:

Why we chose this:

What this enables:

What this prevents:

Confidence:

What evidence would cause us to revisit:
```

---

# 30. Initial roadmap

## Phase 0 — Buildable hypothesis

Goal:
Prove that drawing → polished result feels good.

Deliverable:
A functioning prototype with a convincing transformation.

## Phase 1 — MVP

Goal:
Prove the creation/share loop.

Deliverable:

```text
Draw
→ Polish
→ Reveal
→ Save
→ Share
```

## Phase 2 — AI remix

Goal:
Test whether AI variation materially increases delight and repeat use.

Potential styles:
- Gummy
- Clay
- Plush
- Glossy
- Surprise Me

## Phase 3 — Retention

Goal:
Understand why someone creates again.

Potential features:
- better history/library
- favorites
- recurring characters
- animation
- more styles

## Phase 4 — Monetization

Goal:
Test willingness to pay.

## Phase 5 — Platform depth

Potential:
- native sticker extensions
- sticker packs
- messenger-specific features
- cross-device library

## Phase 6 — Social/creator layer

Only if evidence supports it.

---

# 31. The first build milestone

The first build is not:

> "The app is complete."

It is:

> **One beautiful vertical slice works.**

Target:

```text
Open
 ↓
Draw
 ↓
Polish
 ↓
See result
 ↓
Save
 ↓
Share
```

A user should be able to do this without needing an account.

---

# 31A. MVP asset acceptance criteria

Every generated creation should have a canonical master plus an export strategy.

The canonical master should be:
- square
- transparent
- high resolution (target 1024×1024)
- visually clean at 1× and downsampled sizes
- safe to derive into platform-specific sticker formats

The production pipeline must NOT assume that the 1024px PNG is the final asset for every destination.

A valid MVP transformation should be able to produce a messaging-friendly derivative without materially degrading silhouette, edge quality, transparency, or visual style.

---

# 32. Acceptance criteria for MVP

The MVP is ready for private beta when:

### Drawing
- drawing feels responsive
- undo/redo works
- empty canvas is handled
- drawing data is preserved
- output has reliable transparency

### Transformation
- successful transformation rate is high
- output clearly resembles source doodle
- result has a consistent visual style
- transformation time is acceptable
- failures can be retried

### Result
- output is immediately understandable
- save works
- share works
- user can return to the library

### Product
- no account required
- no unnecessary onboarding
- no complex editing
- primary journey is clear

### Analytics
- activation events work
- creation funnel works
- sharing initiation is tracked
- errors are recorded

---

# 33. First research/validation questions

Even while building, keep these questions alive:

1. What do people naturally draw?
2. What are they trying to communicate?
3. Does the output feel sufficiently "theirs"?
4. Do they prefer faithful transformation or creative interpretation?
5. Does 3D add meaningful delight?
6. How important is speed?
7. When do they share the result?
8. Who do they share it with?
9. What causes a second creation?
10. What part of the experience would they pay for?

---

# 34. Current competitive conclusion

The research does NOT invalidate the idea.

It changes the framing.

We should not enter the market as:

> Another AI sticker maker.

The current working wedge is:

> **A doodle-first expressive creation tool that turns a rough personal mark into a polished, recognizable, visually distinctive sticker.**

Three differentiators should be tested in combination:

```text
DOODLE-FIRST
      +
FAITHFUL POLISH
      +
EXPRESSIVE 3D STYLE
```

The product should initially be standalone and cross-platform, but use the operating system's native sharing path.

Messenger-specific sticker installation can become a later growth and retention layer.

---

# 35. Current product positioning hypothesis

Working positioning:

> **Draw anything. We'll make it sendable.**

Alternative internal framing:

> **Your doodle, polished.**

Longer-term vision:

> **Build your own visual language for conversation.**

Do not finalize marketing language until user research and prototype testing provide evidence.

---

# 36. Immediate next tasks

## Product task

Validate the core creation loop with a prototype.

## Technical task

Investigate the best way to create a faithful 3D transformation from arbitrary 2D doodle input.

## Research task

Continue competitor investigation specifically around:
- doodle preservation
- 3D transformation
- speed
- sharing
- repeat creation
- reaction packs

## Architecture task

Design the transformation engine so local/procedural, AI, and future engines are interchangeable.

## Measurement task

Implement analytics before private beta.

---

# 37. Definition of success for the first iteration

The first iteration succeeds if we can get a small group of people to:

1. open the app,
2. draw something without needing instruction,
3. enjoy the transformation,
4. recognize their own doodle in the result,
5. save or share it,
6. voluntarily make another one.

That behavioral loop matters more than the number of features in the app.

---

# 37A. Immediate Stylization Lab task

The next technical/art-direction milestone is a reproducible Blender Stylization Lab.

### Inputs

- 20 representative doodles
- canonical stroke JSON
- style ID
- style version
- seed
- fixed camera recipe
- fixed lighting recipe

### Outputs

For every doodle/style combination:
- 1024×1024 RGBA PNG master
- 512px sticker preview
- approximately 128px thumbnail/legibility test
- metadata JSON
- render time
- success/failure status

Create a contact sheet for visual review.

### Initial benchmark categories

Include:
- closed blob
- heart
- cloud
- star
- simple face
- stick figure
- object-like doodle
- animal-like doodle
- flower
- open stroke
- scribble
- multiple disconnected strokes
- overlapping strokes
- asymmetrical form
- letter
- number
- tiny doodle
- detailed doodle
- intentionally messy doodle
- deliberately bad doodle

### Evaluation dimensions

Score:
- silhouette fidelity
- recognition
- preservation of quirks
- material quality
- dimensionality
- visual consistency
- sticker legibility
- delight
- shareability
- latency
- reproducibility
- output file quality

### Decision gate

Do not choose a production renderer based on aesthetics alone.

Choose the direction only after comparing:
- procedural
- AI
- hybrid

on the same input corpus and scoring them on the same dimensions.

---

# 38. Guiding principle

> **Build the smallest product that proves the most important behavior, while designing the underlying system so that validated discoveries can be added without rebuilding the product from scratch.**
