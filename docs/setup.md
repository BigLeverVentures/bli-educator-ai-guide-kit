# Provider setup and learner launch

[Home](../README.md) · [Adaptation recipe](adapt.md)

These are educator setup directions. The student sees a short verified launch link
and instructions after the educator has built, checked and published the adaptation.
No platform-independent file format creates a universal install link or supplies a
model account. A link on your own website/LMS opens the chosen provider; it is not
an embedded chat widget. An embedded service would need a separate implementation,
privacy design and inference-cost arrangement.

## Claude

Native plugins require a supported paid Claude plan (Pro, Max, Team or Enterprise).
Organization controls may restrict marketplaces. The guides themselves are free.
The curriculum can also be used in an ordinary conversation without plugins.

For the default kit packages, open Claude → Customize → Plugins → Add → Add marketplace
→ Add from a repository, and enter:

https://github.com/BigLeverVentures/bli-educator-ai-guide-kit

Confirm the repository, sync it if requested, then add the two guides. Labels can
vary; follow [Anthropic's current help](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).
Start a new ordinary Chat and explicitly name the installed guide:

> Use the installed Big Lever Guide Me skill. My task is [describe your task]. Help
> me work through a useful next step.

> Use the installed Big Lever Your Learning Path skill. My learning goal is
> [describe your goal]. Help me choose a small path and explain why it fits.

For an adaptation, use your own distribution repository URL and configured names.
If an earlier BLI guide with the same package name is installed, disable the old
copy while testing to avoid ambiguous activation; you can keep using the existing
student release instead. Distinct schools should use distinct profile slugs.
The repository route needs no student ZIP upload, terminal or API key. Missing
controls are an account/organization access question, not evidence of a broken lesson.

Local package validation does not establish student-account installation or coaching
reliability. Before recommending a deployment, follow the [student journey trial](evaluation.md)
from your actual lesson page with a separate eligible learner account.

## ChatGPT / OpenAI

Each `packages/<name>/` is a portable skills-only package with root `plugin.json`
and a self-contained `skills/` directory. The `builder/<role>/` files provide the
human-readable instructions, name/description/starters in `settings.json`, and one
combined `knowledge.md` for an authoring surface that supports those fields.
Do not send students those authoring files as if they were a published assistant.

Use the authoring/import method actually available in your OpenAI account. The
[portable plugin](https://github.com/BigLeverVentures/bli-educator-ai-guide-kit/tree/main/packages)
packages here are files, not a public OpenAI listing. Public distribution depends
on provider eligibility and review. No public OpenAI install link is supplied by this kit. Check your account's current
creation and distribution options before promising access to learners.

If an educator's authoring surface accepts instructions and Knowledge files, use
`instructions.md` for behavior, the fields in `settings.json` for presentation,
and `knowledge.md` as source material. Review the actual surface's limits; a successful
upload alone does not prove the guide retrieves the curriculum. This is a fallback
authoring recipe, not a claim that a particular retired or gated product is available.

## Gemini — experimental

The same `builder/<role>/instructions.md`, `settings.json` and `knowledge.md` are
available for an educator's private Gem experiment where that account supports
instructions and knowledge. This kit provides no new Gemini install/shared links.
Reliable student coaching and curriculum retrieval are not established for this
experimental adaptation. Do not advertise dependable parity with supported guides.
Run the same failing cases, verify recipient access and knowledge retrieval, and
keep the experimental label unless evidence supports changing it.

## Capabilities and student-facing instructions

File/reference reading is needed for the bundled curriculum. Browsing is useful for
current research; it is optional for lessons that work from supplied text. Code
execution is optional for relevant coding/data tasks. Image generation, external
actions, MCP servers, API keys and Institute telemetry are not required. A guide
cannot turn on a capability or gain private LMS access through instructions.

Give students the guide name, verified provider link or repository route, the
actual account/subscription requirement, and a first message. Explain that the
assistant tab is separate from your lesson. If a plan is useful, the learner copies
it into notes they control and pastes a short handoff into the other guide.

Suggested Version 1 wording (replace the bracketed fields):

> These guides are Version 1. Try them and tell us what helps or gets in your way.
> Send optional feedback to [your support destination], including your goal, which
> guide/provider you used, what happened and what you needed. Share only redacted
> information. The guides do not automatically send your chats to us.

Test the final link with a student account. A provider's share link can be limited
to named recipients or an organization; it is not necessarily public.
