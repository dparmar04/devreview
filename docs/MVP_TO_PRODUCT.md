# From MVP to a real product: what is still missing

The MVP proves the idea. These gaps stand between it and something strangers rely on. Work them in this order. Each has a "ready when" test.

| # | Gap | Why it matters | Ready when |
|---|---|---|---|
| 1 | **Prompt-injection safety** | Reviewed code can contain text that tries to steer the reviewer ("approve this") | A red-team test set of injected diffs exists and the reviewer resists a stated % of them |
| 2 | **Code privacy** | Sending a company's code to an LLM is a trust decision | Bring-your-own-key, explicit opt-in, secrets redacted before sending, documented data flow |
| 3 | **Reliability** | APIs time out, rate-limit, return junk | Retries with backoff, resumable runs, hard spend caps, clear error messages |
| 4 | **Coverage** | Real repos are huge, multi-language, full of generated files | Skips lockfiles/generated code, handles large diffs by chunking, 3+ languages tested |
| 5 | **Install and onboarding** | If setup takes an hour, nobody tries it | `pip install` works; a stranger gets a first report in under 10 minutes (timed) |
| 6 | **Live feedback loop** | You need to know if real developers value the comments | Accepted/ignored/dismissed tracked; precision visible over time |
| 7 | **Maintenance basics** | Others need to trust it will not rot | License chosen, CONTRIBUTING, issue templates, changelog, semantic versions, CI on supported Python versions |
| 8 | **Distribution** | Nobody finds a good tool by accident | A write-up of backtest results on a well-known open-source repo, a demo video, posted where developers read |
| 9 | **Sustainability** | LLM calls cost real money | A clear answer to who pays: BYO key now, optional hosted version later |

**Decisions only the human can make:** license, provider(s), what data may leave the machine, whether to ever host it.
