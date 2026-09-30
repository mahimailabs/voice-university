# Open Voice University

Democratized way of learning about Voice AI from first principle thinking. From research and experimental solutions to applying it to real world problems.

Read the courses at **[mahimai.ca/learn](https://mahimai.ca/learn)**.

## 100x Voice Engineer

- [Text to speech](src/content/courses/tts): speech synthesis, evaluation and serving.
- [Speech to text](src/content/courses/stt): recognition, data, evaluation and adaptation.
- [LiveKit](src/content/courses/livekit): voice agents, telephony and production operation.
- [Component guides](src/content/learn): criteria for evaluating each part of a voice system.

## Repository structure

```text
src/content/courses/   Course lessons and units (MDX)
src/content/learn/     Component guides (MDX)
public/audio/tts/     Lesson audio examples
public/diagrams/      Embedded architecture diagrams
```

This repository owns the learning content. [mahimai.ca](https://github.com/mahimailabs/mahimai.ca) owns the Astro/React renderer, shared lesson components, navigation and interactive tools. MDX imports resolve in that site after syncing; this repository is not a standalone application.

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions arrive through pull requests. Keep changes focused and include sources or reproducible examples for technical claims.

## Private revision phase

This repository is private while the lessons and components are revised. The website’s automatic remote sync is paused; builds use the existing committed content snapshot. Lessons already published on mahimai.ca remain visible.

For local previews, clone this repository beside `mahimai.ca`, then run from the site:

```sh
pnpm university:sync:local
pnpm dev
```

Sync replaces the managed directories: edit lessons here, not in the site’s mirrored copy. Do not commit private drafts to the website repository until they are ready to publish.

When the revisions are ready, make this repository public and re-enable `tsx scripts/sync-university.ts` before Astro in the website build command. A content merge alone does not trigger a site deployment.
