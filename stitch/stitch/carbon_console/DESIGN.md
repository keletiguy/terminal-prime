# Design System Specification: Technical Precision & Tonal Depth

## 1. Overview & Creative North Star: "The Kinetic Monolith"
The Creative North Star for this design system is **"The Kinetic Monolith."** 

This system rejects the "web-template" aesthetic in favor of a high-performance, desktop-native feel inspired by technical Linux environments and professional financial terminals. It avoids the frailty of thin lines and white space, opting instead for a sense of structural density, interlocking "plates" of color, and purposeful asymmetry. We create premium quality not through decoration, but through the extreme precision of our spatial relationships and the intentional "weight" of our UI elements.

## 2. Colors & Surface Architecture
We move away from flat design by treating the screen as a physical stack of machined surfaces.

### The Color Palette
*   **Neutral Base:** `surface` (#131313) provides the foundation.
*   **Primary Action:** `primary_container` (#1f538d) is our signature vibrant blue, used for high-impact interaction.
*   **Semantic Intelligence:** 
    *   **Success (Paid):** `tertiary` (#fdbb2e - adjusted to Amber/Gold) and custom green tones.
    *   **Error (Overdue):** `error` (#ffb4ab).
    *   **Warning (Partial):** `tertiary_container` (#6d4c00).

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders to section off the UI. 
Boundaries are defined exclusively through background shifts. A sidebar isn't "separated" by a line; it is a `surface_container_low` slab sitting adjacent to a `surface` workspace. This creates a more cohesive, high-performance look that reduces visual noise.

### Surface Hierarchy & Nesting
Use the "Stacking Principle" to define importance. The deeper the container, the darker or more "sunken" it feels.
*   **Base Layer:** `surface` (#131313).
*   **Main Content Blocks:** `surface_container` (#20201f).
*   **Active/Interactive Cards:** `surface_container_high` (#2a2a2a).
*   **Floating/Global Modals:** `surface_bright` (#393939).

### The "Glass & Gradient" Rule
To elevate the "CustomTkinter" inspiration into a premium space:
*   **CTA Soul:** Do not use flat blue for primary buttons. Apply a subtle linear gradient from `primary` (#a5c8ff) to `primary_container` (#1f538d) at a 145-degree angle.
*   **Instrument Glass:** For floating tooltips or overlay panels, use `surface_container_highest` at 80% opacity with a `20px` backdrop-blur.

## 3. Typography: Editorial Authority
We utilize **Inter** for its mathematical precision and exceptional readability at small scales.

*   **Display (Large Data Points):** Use `display-lg` (3.5rem) with `-0.02em` letter spacing. This is for primary financial totals.
*   **Headline (Section Headers):** `headline-sm` (1.5rem) should be used sparingly to define major modules.
*   **Title (Functional Labels):** `title-md` (1.125rem) handles the bulk of the navigational work.
*   **Body (Technical Data):** `body-md` (0.875rem) is the workhorse. Ensure line-height is generous (1.5) to maintain legibility against the dark background.
*   **Labels (Metadata):** `label-sm` (0.6875rem) in `on_surface_variant` (#c2c6d1) should be all-caps with `0.05em` tracking for a "technical readout" feel.

## 4. Elevation & Depth: Tonal Layering
Traditional shadows are too "soft" for this technical aesthetic. We use **Tonal Layering** and **Ambient Glows**.

*   **The Layering Principle:** Depth is achieved by placing `surface_container_lowest` (#0e0e0e) elements *inside* `surface_container` modules to create "wells" for input fields, or placing `surface_container_highest` elements on top to represent "raised" buttons.
*   **The Ghost Border:** If high-contrast separation is required for accessibility, use `outline_variant` (#424750) at **15% opacity**. It should be felt, not seen.
*   **Technical Glow:** Instead of a black shadow, use a 4px blur of `primary_container` at 10% opacity behind active primary elements to simulate a subtle LED glow from the "display."

## 5. Components: Machined Precision
All components must adhere to the `DEFAULT` roundedness of **10px (0.5rem)** to maintain the CustomTkinter DNA.

### Buttons
*   **Primary:** Gradient fill (Primary to Primary Container). On hover, increase the brightness of the `surface_tint`.
*   **Secondary:** `surface_container_highest` fill with no border. Text in `on_surface`.
*   **Tertiary:** No fill. Text in `primary`. Hover state triggers a `surface_container_low` background.

### Input Fields
*   **Structure:** Use `surface_container_lowest` for the field background to create a "recessed" look. 
*   **State:** On focus, the "Ghost Border" becomes 100% opaque `primary` (#a5c8ff).

### Cards & Lists
*   **Strict Rule:** No dividers. Use **Spacing Scale 4 (0.9rem)** to separate list items. 
*   **Grouping:** Group related items onto a single `surface_container` slab.

### Financial Status Indicators (The "Status Pill")
*   **Paid:** Small chip using `on_tertiary_container` (#fcba2d) text on a `tertiary_container` background.
*   **Overdue:** `on_error_container` text on `error_container`.
*   **Interaction:** These are never interactive; they are "read-only" indicators of system state.

### Technical Data Grid
*   A custom component for financial logs. Use `surface_container_low` for even rows and `surface` for odd rows to create a "Zebra" effect without using lines.

## 6. Do's and Don'ts

### Do
*   **DO** use asymmetry. If a dashboard has three widgets, let one take up 60% of the width to create an editorial feel.
*   **DO** use the Spacing Scale religiously. Consistent gaps of `2.5 (0.5rem)` or `5 (1.1rem)` are what make the system feel "engineered."
*   **DO** use `backdrop-blur` on scrolling headers to maintain a sense of layered depth.

### Don'ts
*   **DON'T** use pure black (#000000) or pure white (#FFFFFF). Use the provided surface and "on-surface" tokens.
*   **DON'T** use standard drop shadows. If it looks like it's "floating in space," it's wrong. It should look "mounted" or "stacked."
*   **DON'T** use 1px borders. If you feel the need for a line, try a 4px gap of the background color instead.