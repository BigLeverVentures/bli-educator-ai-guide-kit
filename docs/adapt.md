# Adapt the guides for your teaching

[Home](../README.md) · [Setup](setup.md) · [Evaluation](evaluation.md)

Start with one useful learner situation, such as preparing a factual volunteer
invitation. Decide what the learner should understand and choose, not just what
artifact the model should produce. Both guides should help with that same situation.

## First, build the complete example

Follow the README clone/check commands, then build `profiles/example-school.json`
to a fresh directory outside the repository. The example includes two short lessons,
complete prompts, learner choices and a changed-case check. Open
`curriculum/example-school/lessons.md`, then read both generated instruction files.
The learner does not need to run the build.

For a quick private example trial, open a fresh ordinary conversation in your
chosen assistant. Paste the generated `builder/guide-me/instructions.md` as your
first message, saying that you want to try these instructions with fictional data.
Attach its `knowledge.md` as reference material if your chat supports files;
otherwise paste the small example's `catalog.json` and `lessons.md` in the next
message, labeling them as reference content. Then send the trial prompt below.
Repeat in a separate fresh conversation with `builder/learning-path/instructions.md`
and its knowledge. This is a chat-based teaching probe, not proof of native plugin
installation. For native testing, publish the generated example marketplace to your
own repository and follow [Claude setup](setup.md) using that URL. The default Big
Lever repository installs the Big Lever profile, not your local example build.

In the example's Guide Me, try: “Why shouldn't I say all volunteers prefer Saturday
mornings when two said they can attend this Saturday?” Expect a direct explanation
of the evidence limit and a concrete next step, without intake.

In Your Learning Path, try: “I need a volunteer invitation. I'm comfortable sending
messages, but I haven't said anything about AI experience. Give me one next action
and a short Guide Me handoff.” Expect the invitation lesson and a small handoff,
without a claim that unassessed AI skills are mastered. The example.org URLs are
illustrations; its supplied lesson bodies are usable for this synthetic trial.

## Make an educator profile

Copy `profiles/example-school.json` to `profiles/my-school.json`. Edit that copy:

| Field | What to supply |
| --- | --- |
| organization | Your learner-facing organization name |
| slug | A short lowercase identifier, such as `my-school`; it identifies packages |
| version | Your release version, such as `1.0.0`; increment after material changes |
| snapshot_date | Curriculum snapshot date as YYYY-MM-DD; must match catalog.json |
| homepage | Your real HTTPS guide/setup page |
| privacy_url, terms_url | Your real deployment policies; empty is allowed for local examples, but fill before student deployment |
| feedback_email | Your voluntary learner support/feedback address; empty means none configured |
| curriculum_dir | Your source folder inside this repository |
| reference_files | Only Markdown/JSON reference files to include, each relative to that folder; use letters, digits, hyphens, underscores, dots and forward slashes, without spaces |
| curriculum_index | Your `catalog.json` reference filename |
| future_courses | Titles of actual planned courses, or an empty list |

Replace the entire example curriculum folder with your material. Changing an
organization name does not rewrite Big Lever's lessons or replace their underlying
methods. Only use content you have permission to adapt and upload to the provider.
Keep private student records and transcripts out of profiles and curriculum files.

## Describe your curriculum once

Copy the example folder to `curriculum/my-school/`. Edit its `catalog.json` and
`lessons.md`, then point your profile at the new folder. A catalog has
`snapshot_date` and a nonempty `resources` list. Each resource has exactly:

```json
{
  "id": "email",
  "title": "A clear volunteer invitation",
  "group": "Useful writing",
  "url": "https://example.org/learning/volunteer-invitation",
  "source_heading": "Resource: email"
}
```

Replace the fictional URL with a real lesson destination. In `lessons.md`, include
`# Resource: email` followed by that lesson's usable body. Preserve exact lesson
prompts, necessary context, inputs, task-specific checks, learner correction and
transfer guidance. The builder checks that every catalog entry has a matching body
heading; it does not judge teaching quality or prove a URL is accessible.

Add a curriculum license/attribution file and list it in `reference_files`. A lesson
link alone cannot substitute for a body the guide needs to read. If some lesson
text cannot be bundled, narrow the catalog to available material or clearly supply
a lawful accessible source through a separately tested integration. Do not pretend
the guide has read a private LMS page. Future courses belong in `future_courses`,
not as invented completed lessons in the body collection.

## Adapt the teaching method deliberately

`templates/common.md` is shared by both guides. The two role files define coaching
and curriculum design separately. Keep direct help, proportionate Socratic questions,
learner-selected corrections, evidence boundaries and uncertainty about placement.
Avoid hardcoding catalog counts or lesson routes in templates; use curriculum
references so each school can change its material without rewriting both roles.
The build gives authoring instructions an 8000-character budget and rejects unresolved
`{{fields}}`. New template variables require a corresponding builder change.

## Build, check, test, release

```sh
python3 -B tools/build.py --profile profiles/my-school.json --output /tmp/my-school-guides-v2
python3 -B tools/test_build.py
```

Inspect the output, follow [provider setup](setup.md), and run the
[coaching scenarios](evaluation.md) with synthetic facts. Try both guides from a
separate learner account and an unfamiliar learner's normal entry page. Fix and
rerun failing cases before calling the adaptation supported. Keep observed results
separate from editorial judgment and tests that only check files.

For your own repository marketplace, copy only the generated `packages/` and
`.claude-plugin/` plus the license/notices into a separate distribution repository,
or maintain those generated folders in your fork as this repository does. Preserve
all curriculum and kit notices. Link students to the provider's verified launch
route and give its subscription requirement. Students should not have to build,
install Git, or upload ZIPs.

For a fork that distributes your school profile, replace the generated folders and
manifest as described in [maintenance](maintenance.md), then verify that same profile:

```sh
python3 -B tools/verify.py --profile profiles/my-school.json
```

Change the verifier step in `.github/workflows/checks.yml` to use that profile too.
The default verifier/CI targets the supplied Big Lever distribution; it should fail
if you compare a different school's output against Big Lever's profile. Keep both
provided profiles as build-test fixtures even when your distribution uses another.

Before public student deployment, replace example.org links, empty policy fields,
example branding and support settings. Record your changes and attribution. Keep
the kit/adapted guides free to access under [the teaching-use license](../LICENSE.md).
