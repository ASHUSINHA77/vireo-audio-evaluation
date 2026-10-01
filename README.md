# Vireo Support Signals

Small, local, dependency-free prototype for exploring support tickets. It reads `tickets.csv` and optional `agents.csv` from `data/`, produces weekly complaint summaries and an agent workload view, and never sends ticket text to a third party.

## Run

Requires Python 3.9+; no package installation is needed.

1. Put the supplied CSV files in `data/` (or run `python app.py --tickets path/to/tickets.csv --agents path/to/agents.csv`).
2. Run `python app.py`.
3. Open the local address printed in the terminal (default `http://127.0.0.1:8765`).

The input column names are detected from common names. If detection fails, add the actual header to the matching alias list near the top of `app.py`. Run `python app.py --help` for options.

## What it does

- Groups tickets by week and assigns each opening message one explainable keyword-rule theme (connectivity, battery/charging, audio, fit, delivery, returns, setup, device fault, or other). It also surfaces frequent terms. This is a prototype classifier, not a claim that a generative model interpreted every ticket.
- Shows tickets closed per agent alongside assignment count, ticket mix, and elapsed time where available. It is a workload view, not an individual performance ranking. Raw closed counts are not comparable without hours, shift, channel, complexity, tenure, and reopen context.
- Shows missingness, duplicate IDs, date coverage, and a sample of source rows so an operator can check what the analysis is based on.

## Current limitations / evaluation

This workspace did not contain the Vireo data pack when this prototype was built. No Vireo-specific findings, financial estimates, or accuracy rates are asserted. Before operational use, map the actual columns, manually label a stratified sample of at least 200 tickets for theme and sentiment, and publish per-theme precision/recall plus the share of tickets that cannot be confidently assigned. Recheck monthly and after taxonomy changes. The app has no external model call; all text remains in the local process.

## Decisions and scope

Prioritized a local, inspectable weekly signal tool and a contextual workload view. Deferred calibrated sentiment, root-cause causal analysis, agent ranking, cost-of-failure estimates, and integrations because the dataset and policy needed to substantiate them were unavailable. The intended operating goal is to select one preventable complaint after measuring its actual baseline and policy cost; a numeric target must not be invented from absent data.
