# Evaluate the guides and the learner journey

Version 1 is for feedback and improvement. File checks, editorial review, model
behavior, independent student access and human learning are different evidence.
Do not use a clean build or model role-play as proof of all of them.

## Automated checks

Run `python3 -B tools/test_build.py` and `python3 -B tools/verify.py` from a clean
checkout. The suite covers both profiles, exact reference inclusion, deterministic
builds, source-change propagation, package metadata and missing/malformed/unsafe
inputs. It verifies failure preserves existing output and catches stale, missing,
extra and forged-manifest generated files. The importer has link-resolution checks.
These checks cannot prove curriculum quality, accessible URLs or model compliance.

## Coaching cases

[tests/coaching-cases.json](../tests/coaching-cases.json) supplies synthetic prompts,
expected behaviors and failure markers. Run each in a fresh conversation with the
intended guide and the selected profile's knowledge. Some cases have a follow-up;
send it only after observing the first response. Do not manufacture a successful
transcript. Capture date, provider/interface, model if shown, profile/package version,
input, actual response, judgment and residual limitation. Keep private learner data out.

The cases cover immediate factual help, novice support, learner-selected correction,
execution-only work, evidence-scoped claims, small paths, unassessed placement,
future-course navigation and unavailable source content. A case is a failure if
its material behavior fails even when the answer sounds polished. After a fix,
rerun that case and another case that could regress.

To evaluate added value, compare with a competent ordinary request using the same
facts and tools. Judge useful work, learner decision quality, effort and transfer
separately. A stronger artifact alone does not establish a stronger learning outcome.
For a human trial, observe whether an unfamiliar learner can start, make a correction,
keep a useful result and apply the method to another case. Obtain appropriate consent;
do not require sharing private work or claim results that have not been observed.

## Full student journey

Start on the educator's saved website/LMS page, using a separate student account:

1. Open the listed guide link or repository setup route; confirm access and any
   subscription requirement match the page.
2. Install/open each guide, start a fresh ordinary chat and send its first message.
3. Ask about an exact supplied lesson and check the guide uses the actual body and
   catalog link, rather than inventing access from a URL.
4. Complete the factual-help, critique-choice and small-path cases. Copy a plan and
   carry a redacted handoff to the other guide manually.
5. Confirm optional feedback is clear and no automatic collection is implied.
6. Repeat from the starting page in a fresh session, correcting unclear directions
   and rerunning any failures. Phone usability is a separate check if advertised.

## What the kit does and does not establish

Build checks establish reproducible file packaging and source fidelity. They do not
establish native provider installation, live model compliance, unfamiliar-educator
completion, phone usability or human learning benefit. Run those trials for your
own adaptation and retain records privately. Share only a deliberately prepared,
consented and redacted public result when that serves your learners.

ChatGPT public distribution depends on provider eligibility and review. Gemini
remains experimental. Do not claim universal compatibility, provider ranking or
learning superiority from package checks alone.
