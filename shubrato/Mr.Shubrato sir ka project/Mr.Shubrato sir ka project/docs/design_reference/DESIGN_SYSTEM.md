---
name: Sanctuary Quietude
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#41484b'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#71787c'
  outline-variant: '#c1c7cb'
  surface-tint: '#3f6372'
  primary: '#00222d'
  on-primary: '#ffffff'
  primary-container: '#0f3846'
  on-primary-container: '#7ca1b2'
  inverse-primary: '#a6ccde'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#46000e'
  on-tertiary: '#ffffff'
  tertiary-container: '#6e001c'
  on-tertiary-container: '#ff6c7a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c2e8fa'
  primary-fixed-dim: '#a6ccde'
  on-primary-fixed: '#001f29'
  on-primary-fixed-variant: '#264b5a'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#ffdada'
  tertiary-fixed-dim: '#ffb3b6'
  on-tertiary-fixed: '#40000c'
  on-tertiary-fixed-variant: '#920028'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-hero:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  display-hero-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: 0em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 17px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: 0em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-caps:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.06em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-mobile: 0.75rem
  margin: 1.25rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.25rem
---

## Brand & Style

This design system establishes a discreet, protective, and trauma-informed interface designed primarily for women, adolescent girls, and vulnerable individuals navigating crisis, journey safety, peer support, and verified reporting. 

The aesthetic is anchored in grounded reassurance rather than anxiety-inducing alarmism. Visual weight shifts away from harsh caution signage toward quiet dignity, clarity, and rapid legibility under acute cognitive overload.

### Design Movements & Tone
- **Trauma-Informed Minimalism:** Generous structural breathing room, deliberate visual hierarchy, and an absence of loud decorative noise that could trigger cognitive panic.
- **Protective Tactility:** Soft, rounded interactive elements with tangible hit states that offer physical certainty during shaky-handed or high-adrenaline interactions.
- **Privacy-First Utility:** Always-visible rapid exit affordances, subtle decoy toggles, and neutral surface appearances that do not immediately signal distress software to onlookers.

## Colors

The palette is engineered to calm nervous system arousal while preserving immediate operational contrast for emergency mechanisms.

- **Primary Anchor (`#0F3846` - Deep Sanctuary Teal):** Emits structural stability, depth, and protective authority. Used for primary navigation, critical headers, and primary active states.
- **Secondary Safe Accent (`#0D9488` - Grounding Sage Teal):** Communicates active safety, verified networks, and reassurance. Used for verification badges, active tracking states, and positive confirmations.
- **Tertiary Controlled Alert (`#E11D48` - Controlled Rose Coral):** A deliberate replacement for strident crimson warnings. Reserved strictly for SOS triggers, panic inputs, and high-urgency confirmations without inducing paralyzing dread.
- **Neutral Canvas (`#64748B` - Slate Neutral):** Provides secondary text definition and quiet structural lines. Backed by parchment/cream surface tints (`#F8FAFC` to `#F1F5F9`) to eliminate stark, clinical white glare.

### Semantic Surface Rules
- Base backgrounds employ warm parchment-slate (`#F8FAFC`) to minimize contrast strain in dark or concealed settings.
- Destructive and emergency actions use `#E11D48` against quiet tinted backgrounds (`#FFE4E6`) rather than pure saturated blocks, preserving optical calm until direct interaction occurs.

## Typography

The typography leverages **Plus Jakarta Sans** across all roles to maintain warm, geometric clarity with accessible optical apertures. It eliminates ambiguity between easily confused characters (e.g., uppercase `I`, lowercase `l`, and digit `1`), which is critical during urgent address entry or resource lookup.

### Behavioral Directives
- **Stress-Resistant Line Heights:** Body typography enforces generous line heights (1.5x - 1.6x) to avoid visual crowding for users experiencing tunnel vision or physical distress.
- **Caps Discipline:** Uppercase styling is strictly reserved for `label-caps` (such as verification status or timestamps) and never applied to long sentences or error banners, preventing the sensation of an aggressive, scolding tone.

## Layout & Spacing

The layout is constructed on a fluid 4-column system for mobile viewports, expanding to 8 columns on tablet devices.

### Form Factor Adaptations
- **Mobile Handheld (320px - 599px):** Canvas padding rests at `margin-mobile` (`1rem`). Structural elements utilize 4 fluid columns with `gutter-mobile` (`0.75rem`) to maximize touch target width while preventing content from hugging the hardware edges.
- **Tablet / Large Handheld (600px - 899px):** Canvas padding increases to `margin` (`1.25rem`), utilizing an 8-column configuration with `gutter` (`1rem`) to keep emergency action cards within thumb reach.

### Reachability and Ergonomics
- **Bottom 40% Priority:** High-stakes interactive triggers (SOS, Live Sharing, Quick Exit) must always reside within the natural one-handed reach zone (the lower 40% of the viewport).
- **Persistent Safe Bounds:** All views account for persistent safe area insets at top and bottom, preventing accidental dismissal gestures or overlay clipping during emergency usage.

## Elevation & Depth

Visual hierarchy relies on soft tonal containment rather than high-contrast structural drops or floating planar shadows. This avoids spatial confusion and keeps surfaces grounded.

### Surface Elevation Hierarchy
- **Level 0 (App Canvas):** Muted slate parchment (`#F8FAFC`). Pure flat baseline.
- **Level 1 (Content Surfaces & Cards):** Pure neutral white (`#FFFFFF`) with a continuous 1px micro-border tinted in `#E2E8F0`. Shadows are absent or limited to an ambient perimeter glow: `0px 2px 8px rgba(15, 56, 70, 0.04)`.
- **Level 2 (Active Sheets & Resource Modals):** Tinted warm white elevated by an ambient diffused shadow: `0px 8px 24px rgba(15, 56, 70, 0.08)`, bounded by a 1px border of `#CBD5E1`.
- **Level 3 (Emergency Floating Trigger / SOS Bar):** Prominent floating status requiring definitive separation. Features a directional soft projection: `0px 12px 32px rgba(225, 29, 72, 0.16)`, framed by a subtle protective inset ring to guarantee separation over live maps or dense directories.

## Shapes

The design system adopts a rounded curvature approach (`roundedness: 2`, base radius `0.5rem` / 8px). 

### Corner Geometry Tokens
- **Base Components (Inputs, Small Badges, Chips):** `0.5rem` (8px). Delivers a friendly, approachable touch without appearing childish or informal.
- **Surface Cards & Action Panels (`rounded-lg`):** `1rem` (16px). Creates soft, welcoming informational boundaries that gently cradle sensitive data and contacts.
- **Persistent Emergency Trays & SOS Action Buttons (`rounded-xl`):** `1.5rem` (24px) up to full pill shapes (`9999px`). Provides smooth, tactile ergonomics for critical, rapid press interactions.

## Components

### Buttons
- **Primary Safety Action:** Background `#0F3846`, text `#FFFFFF`, rounded `1rem`. Minimum touch height of 52px to prevent missed taps under acute motor stress.
- **Controlled SOS Trigger:** Dual-state action button. Neutral resting state: `#FFE4E6` border with `#BE123C` text. Depressed/Hold state: solid `#E11D48` background with tactile countdown ring and continuous haptic feedback.
- **Secondary / Calm Outline:** Background `#F8FAFC`, border 1px solid `#CBD5E1`, text `#0F3846`.

### Quick Exit Utility (Safety Critical)
- Anchored permanently to the top or bottom right header margin.
- Styled as a distinct high-contrast, non-stigmatizing pill: `#0F3846` text on `#F1F5F9` background with an exit glyph and explicit text ("Quick Exit").
- Single-tap execution immediately replaces the viewport with a decoy utility screen (e.g., weather or neutral calculator) and flushes the backward navigation cache.

### Verification Badges & Timestamp Tags
- **Trusted Service Tag:** Subtle sage pill using `#F0FDFA` background, `#0D9488` text, and a micro-check icon.
- **Timestamp Ledger:** Strict `label-caps` font in `#64748B` accompanied by a localized verification stamp ("Verified 12m ago") to ensure users can assess source currency without cognitive fatigue.

### Cards & Resource Containers
- Constructed on `#FFFFFF` with `rounded-lg` (16px) corners and a 1px `#E2E8F0` border.
- Cards separate critical details (phone, physical address, distance, operating hours) into scannable horizontal micro-rows with ample line spacing.

### Form Inputs & Checkboxes
- **Input Fields:** Generous 48px height, filled `#F8FAFC` base, transitioning to a 1.5px `#0D9488` focus ring with no jarring layout shifts. Placeholder text is written in reassuring, conversational language.
- **Selection Controls:** Checkboxes and radios feature 24px touch footprints with soft 6px rounded edges for checkboxes, eliminating harsh, clinical square motifs.

### Confidential Reporting Modules
- Incorporates progressive single-question flows to prevent cognitive overload.
- Includes a persistent "Clear Form Trace" trigger and non-judgmental prompt language without interrogative or accusatory phrasing.