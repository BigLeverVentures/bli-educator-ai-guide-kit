# Big Lever Institute AI Guide Kit for Educators — Version 1

Build two AI learning guides around your teaching material:

- **Guide Me:** a coach, research assistant and thought partner for questions,
  exercises, critique and useful work. Learners can start without an intake.
- **Your Learning Path:** a conversational curriculum designer that recommends a
  small path, explains the fit and gives the learner a plan they can change.

The kit includes both guides, their teaching method, a curriculum snapshot, an
adaptation recipe, a fictional-school example, reproducible packages and checks.
It is free to adapt and share **for teaching**, subject to the [teaching-use
permissions](LICENSE.md). Do not sell or charge for access to the covered kit or
adapted guides. The default curriculum now has a teaching-use notice too; prior CC BY rights in unchanged material remain valid regardless of the copy used.

## Choose your route

**Use Big Lever's existing student guides:** start at
[Your Big Lever AI Guides](https://bigleverinstitute.org/guides) and the
[student installation repository](https://github.com/BigLeverVentures/bli-ai-guides).
Those are separate from this educator toolkit.

**Build guides for your own learners:** follow the
[adaptation recipe](docs/adapt.md), beginning with the fictional-school example.
You do not need to use the Big Lever curriculum.

**Want lessons without AI guide tooling?** Use the independent
[curriculum package](https://github.com/BigLeverVentures/bli-for-educators) or
[read the lessons](https://exercises.bigleverinstitute.org/).

## Try the build recipe

Educators or their technical helpers need Git and Python 3.10 or newer. Students
need neither. No Python dependencies, API keys or Institute model server are needed.
From a terminal:

```sh
git clone https://github.com/BigLeverVentures/bli-educator-ai-guide-kit.git
cd bli-educator-ai-guide-kit
python3 -B tools/test_build.py
python3 -B tools/verify.py
```

Make a disposable output directory with a name you have not used before:

```sh
python3 -B tools/build.py --profile profiles/example-school.json --output /tmp/my-school-guides-v1
```

The build refuses an existing output directory and never overwrites it. Pick a new
name on a later run. Open the output's `builder/guide-me/instructions.md` and
`builder/learning-path/instructions.md`; each has `settings.json` and a generated
`knowledge.md`. Its `packages/` contains both portable/Claude plugins and its
`.claude-plugin/marketplace.json` connects them. The example school and its links
are fictional; replace them before sharing with learners.

Build the supplied Big Lever profile the same way:

```sh
python3 -B tools/build.py --profile profiles/big-lever.json --output /tmp/big-lever-guides-v1
```

The committed [packages](packages) and [authoring files](builder) are generated
from that profile. Edit `templates/`, `profiles/` and the selected `curriculum/`
source, then rebuild; do not maintain the generated copies independently.

## Put guides on your learning site

Publish an educator-owned provider guide or marketplace, test it with a learner
account, and put its verified link and short setup directions in your website or
LMS. [Provider setup](docs/setup.md) separates this educator task from student use.
A GitHub repository is source/package distribution, not an embedded chat service or
a universal one-click assistant link. Students use their own provider accounts and
any subscription its features require. No ZIP handoff is needed for the Claude
repository route.

Claude packages are included. ChatGPT authoring and portable package files are
included, but public distribution still depends on OpenAI eligibility/review;
this repository does not bypass that process. Gemini remains experimental and
is not presented as dependable student coaching. See [test evidence and limits](docs/evaluation.md).

## Curriculum and updates

Both roles use one curriculum folder. This kit's default snapshot comes from the
same [public educator curriculum](https://github.com/BigLeverVentures/bli-for-educators),
not a separate lesson-authoring stream. The initial public snapshot is dated
2026-10-17; see [upstream provenance](curriculum/big-lever/upstream.json).
Installed guide references are dated copies. [Maintenance](docs/maintenance.md)
explains importing a reviewed update, rebuilding both roles and releasing it.

## Reuse and feedback

You may adapt and share covered kit materials for teaching, including on your own
site and around your own curriculum. Ordinary compensated teaching/tuition is
allowed; selling the kit or charging specifically for adapted guide access is not.
Learner-created work can be used professionally or commercially. The public
curriculum is offered here under teaching-use terms; prior CC BY rights in unchanged material remain valid regardless of the copy used. Read [permissions examples](docs/permissions.md),
the [license](LICENSE.md) and [attribution boundaries](NOTICE.md).

Version 1 is an invitation to try the kit and tell us what helps or gets in your
way. Open a [public issue](https://github.com/BigLeverVentures/bli-educator-ai-guide-kit/issues)
with fictional/redacted examples, or email **help@bigleverinstitute.org**, subject
**Educator AI Guide Kit Version 1 feedback**. Include your goal, guide/provider,
what happened and what you needed. Do not submit private student work. This kit
has no automatic chat collection or feedback sending. Your AI provider has its
own data practices. [Institute privacy](https://bigleverinstitute.org/privacy).

Educational direction: Chris Myers. Development and drafting: Codex, working with
Chris. [Teaching approach](docs/pedagogy.md) · [Contributing](CONTRIBUTING.md).
