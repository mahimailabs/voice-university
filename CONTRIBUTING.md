# Contributing

## Make a change

1. Fork this repository and create a branch.
2. Edit an existing MDX lesson or use a neighboring lesson as a template.
3. Preserve existing filenames, frontmatter and lesson anchors unless you also coordinate the route change with the website.
4. Open a pull request describing the learner’s problem, your change, and any evidence or preview screenshots.

## Lesson structure

Start with a concrete problem. Use short technical headings, explain one idea at a time, and include a practical exercise where useful. Separate measured results from estimates. Cite primary sources for implementation details and preserve attribution for third-party material.

A suggested interactive lesson flow is **Listen → Predict → Experiment → Explain → Build**. The site renderer must support a component before it can be used here; new WaveSurfer/Gradio integrations are not yet installed.

Course frontmatter includes `course`, `courseTitle`, `order`, `title` and `summary`. Existing lesson-per-page courses also use `unit` and `unitTitle`; unit-per-page courses use `lessons`. The authoritative schema is [src/content.config.ts in the site repository](https://github.com/mahimailabs/mahimai.ca/blob/main/src/content.config.ts).

Keep current relative imports of shared Astro components: their paths are resolved after the files are copied into the website. Propose new shared components in the website repository as a companion change.

## Preview

Clone `voice-university` and `mahimai.ca` as sibling directories. Install the website dependencies with `pnpm install`, then run `pnpm university:sync:local` and `pnpm dev` from `mahimai.ca`. Run the sync command again after editing a lesson. Never put credentials, private recordings or client data into a contribution.

Audio and diagrams should include provenance and permission to redistribute. Existing materials retain their existing rights and attribution; no blanket license is granted for third-party material.
