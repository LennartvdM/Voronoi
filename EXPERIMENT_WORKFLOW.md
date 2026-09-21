# Experiment workflow

Each visual experiment is an immutable mark. Animation quality is judged from a
live deploy, so an unreviewed idea must never replace or edit an earlier mark.

## One iteration

1. Start a fresh branch from the latest integration branch. Do not stack a new
   experiment on a previous experiment branch.
2. Choose a unique mark name before creating files.
3. Add only `<mark>.html` and `tests/<mark>/build.py` in the experiment PR.
   The builder must emit its own mark and must not rewrite `index.html`, another
   mark, or another mark's tests/results.
4. Build twice and compare the outputs to prove generation is deterministic.
5. Push the branch and use its deploy-preview URL to judge the animation.
6. Record the outcome without rewriting history: merge an accepted mark, or
   close a rejected mark's PR. Do not promote an unreviewed mark in the gallery.

## Promotion

After a mark passes live review, use a separate, small promotion PR to add its
card to `index.html`, add measured results, and label the previous accepted mark
appropriately. Keeping promotion separate prevents every experimental branch
from conflicting on the shared gallery.

## Updating an open experiment

Before pushing another revision, fetch and rebase onto the latest integration
branch. If the experiment has already been rejected, close its PR and start the
next idea from the latest integration branch under a new mark name instead of
adding corrective commits to the rejected branch.

Typical commands (replace `origin/main` and the mark name as needed):

```bash
git fetch origin
git switch main
git pull --ff-only
git switch -c experiment/<mark>
python3 tests/<mark>/build.py
cp <mark>.html /tmp/<mark>.html
python3 tests/<mark>/build.py
cmp -s <mark>.html /tmp/<mark>.html
git add <mark>.html tests/<mark>/build.py
git commit -m "feat: add <Mark> experiment"
git push -u origin experiment/<mark>
```
