# Learning tracker

You only get the skill if you can prove it. A row is DONE when its proof exists, not when the agent says so.

## Skill proof table
| Skill | Proof required | Phase | Done? |
|---|---|---|---|
| Git internals (history, diff, blame) | Fixture test for introducing-commit finder passing; you explain SZZ aloud | 1 | |
| Golden datasets and label noise | Dataset committed + noise rate in `docs/DATASET_AUDIT.md` | 1 | |
| Calling an LLM safely | Fake-client tests, live test excluded from verify, spend cap works | 2 | |
| Evals (metrics) | `docs/BASELINE.md` with recall, false alarms, cost per bug caught | 2 | |
| Regression testing for AI | Gate fails on a deliberate regression (show output) | 3 | |
| LLM-as-judge validation | Agreement % recorded in `docs/METRICS.md` | 3 | |
| Security basics | You can name what bandit, pip-audit, secret scan and prompt-injection tests each catch | 0-2 | |
| Tracing | Link to a trace where you found a real bug | 5 | |
| RAG (repo context) | Backtest before/after with a measured difference | 7 | |
| Cost engineering (routing, caching) | Cost per bug caught before/after | 8 | |

## Rules
1. **Every change needs a number.** If a change cannot be measured, you do not yet understand it.
2. **Check yourself questions** come after every task. Answer in your own words; if you cannot, ask again.
3. **Weekly explain-back:** explain one component to a friend (or record 3 minutes) with no notes. What you cannot explain goes in the re-learn list below.
4. **Failures log:** one line per bug or surprise and its real cause. This is where real learning shows up.

## Failures log
| Date | What broke | Real cause | What I learned |
|---|---|---|---|

## Re-learn list
-

## Glossary (plain English; the agent adds new terms here)
- **Eval:** a test suite for AI. Instead of pass/fail you measure how often it is right.
- **Golden dataset / ground truth:** examples where the correct answer is known, used as the answer key.
- **Recall:** of all real bugs, the share the reviewer caught. Like a smoke alarm that rings for real fires.
- **False alarm:** the reviewer flags something on code with no known bug. The smoke alarm ringing at toast.
- **Precision:** of everything it flagged, the share that was a real bug.
- **SZZ:** a classic method that finds the commit that introduced a bug by looking at who last touched the lines a fix removed.
- **Label noise:** wrong answers inside the answer key. It limits how much any score can be trusted.
- **Regression:** something that used to work (or score well) getting worse after a change.
- **Token:** a chunk of text (about three quarters of a word) that an LLM reads or writes; you pay per token.
- **Prompt injection:** hidden instructions inside the data an AI reads ("ignore your rules") that try to hijack it.
- **Hallucination:** an AI stating invented things confidently, such as fake functions, packages or test results.
- **Slopsquatting:** attackers publish malware under package names AI tools tend to invent; installing them runs the attacker's code.
- **Pre-push hook:** a script git runs before `git push`; if it fails, the push stops.
- **CI:** a robot that re-runs all checks on a clean machine whenever you open a pull request.
- **Branch protection:** GitHub settings that physically stop pushes to `main` unless checks pass and a human approves.
- **LLM-as-judge:** a second AI grades the first AI's work. Useless until checked against human grades.
- **Cache (record and replay):** saving an answer so the same question later costs nothing and gives the same result.
- *Coming in later phases:* **RAG** (the AI looks up relevant material and reads it before answering), **BM25** (classic keyword search), **vector search / pgvector** (search by meaning, using a database add-on), **re-ranking** (a final pass that puts the best results first), **router** (easy tasks to a cheap model, hard ones to a strong one), **LoRA** (a cheap way to adapt a small model to your task), **MCP** (a standard way to give an AI tools), **tracing** (a flight recorder for every AI call).
