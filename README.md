# Open Voice University

Democratized way of learning about Voice AI from first principle thinking. From research and experimental solutions to applying it to real world problems.

Read the courses at **[mahimai.ca/learn](https://mahimai.ca/learn)**.

## 100x Voice Engineer

- [Text to speech](src/content/courses/tts): speech synthesis, evaluation and serving.
- [Speech to text](src/content/courses/stt): recognition, data, evaluation and adaptation.
- [LiveKit Mastery](src/content/courses/livekit): voice agents, telephony and production operation.
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

## Local preview

Clone this repository beside `mahimai.ca`, then run from the website:

```sh
pnpm university:sync:local
pnpm dev
```

Sync replaces the managed directories: edit lessons here, then sync to preview. The website keeps a committed content snapshot; merging a contribution here does not automatically deploy the website.

Each published lesson links directly to its source through **Edit this lesson on GitHub**. Fork the repository and propose a focused change using a pull request.
