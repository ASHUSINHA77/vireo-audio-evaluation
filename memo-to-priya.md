# To: Priya Raman, Head of Customer Experience
## Subject: A first weekly view of Vireo support tickets

Priya,

I built a small local prototype that assigns each ticket to one explainable keyword-rule theme, rolls up weekly theme shares and recurring terms, and shows closure counts alongside each agent’s assignment volume and channel mix. It is designed to help a CX lead decide what to inspect next. The theme rules are unvalidated hints, not verified complaint categories. The agent view is intentionally descriptive. Closures alone do not tell us who is “pulling their weight” when shift length, channel, case difficulty, tenure and reopen work differ.

I could not produce Vireo findings or a responsible rupee estimate because the supplied workspace contained none of the referenced files: tickets, roster, reference tables, operating policy, email thread or submission form. The pack names and prompt did not include data contents or the submission URL. I have not inferred a baseline, a policy cost, or a savings target. The prototype is ready to run once `tickets.csv` and `agents.csv` are placed in `data/`; the README gives the command.

**Business goal to validate:** use the first data-backed weekly review to select one preventable complaint, then reduce its share of eligible tickets by **at least 20% relative to its measured baseline within one quarter**. The baseline and rupee value must be calculated from Vireo’s ticket denominators and the cost in its policy before Priya accepts this as a target. A 20% relative reduction is a proposed target, not a measured Vireo result; quoting a rupee amount now would be fabricated.

**How to know the signals are right:** have two reviewers independently label a stratified sample of at least 200 tickets for complaint theme, then adjudicate disagreements. Compare the tool’s assigned themes to that reference set; publish accuracy (and therefore observed error rate), per-theme precision/recall, and the share falling into “Other / inspect.” Reviewers should also check a weekly sample of source messages against the displayed top terms. Recheck monthly and after any taxonomy change. No Vireo-specific accuracy rate can be measured until tickets are available.

**Scope choice:** this first slice includes local weekly exploration, basic data-quality checks and a workload view. It does not claim root cause, causal savings, sentiment accuracy or agent performance. We should add one validated complaint taxonomy and one agreed operating action before expanding the analysis.

Regards,

Vireo evaluation prototype
