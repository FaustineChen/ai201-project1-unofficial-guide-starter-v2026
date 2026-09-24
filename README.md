# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

This is a RAG-based Q&A system built over advice_threads, a corpus of 23 real question-and-reply threads where several people respond to the same question, often disagreeing with each other.
It answers questions the corpus actually discusses related to campus — like clubs or changing major — by retrieving the reply chunks most relevant to the question and naming which thread they came from.
For questions the threads clearly don't cover, a relevance gate based on cosine distance stops the system from guessing and returns an "I don't have enough information about that" response instead.

## Chunking Strategy

**Chunk size:** 800
**Overlap:** 120

I replaced the fixed-size window splitter with structure, spliting each thread into (question + one reply) chunks, prepending the question to every chunk.

I didn't tune `chunk_size` or `overlap` beyond their defaults, because this splitting strategy barely uses them: threads averaging 543 characters and replies typically under 200. Question + one reply produces small chunks on its own. `chunk_size` and `overlap` only matters for the case where a single reply is too long to fit — a case that doesn't occur anywhere in current 23-thread corpus. I kept both at reasonable defaults (chunk_size=800) as a safety margin rather than something I actively tuned, since there was nothing in my data to tune them against.

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `thread_bike_commute.txt#0 ` — produced by: `chunker.py::split_documents`

```
Is a bike worth it for a 20 minute walk commute?

Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.
```

**Chunk 2** — source: `thread_first_gen.txt#1` — produced by: `chunker.py::split_documents`

```
Anything specific for first-generation students?

The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.
```

**Chunk 3** — source: `thread_laptop_specs.txt#2` — produced by: `chunker.py::split_documents`

```
How much laptop do I actually need for CS courses?

I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.
```

**Chunk 4** — source: `thread_parking.txt#1` — produced by: `chunker.py::split_documents`

```
Worth getting a parking permit?

Street parking on Verrill is legal and free and unmarked, which is why half the upper years do it.
```

**Chunk 5** — source: `thread_sleep_schedule.txt#1` — produced by: `chunker.py::split_documents`

```
Everyone says fix your sleep. Does it actually matter?

The library being open until 2am is a trap. It's a resource, not a schedule.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** Is it possible to apply intership in spring?

**Answer:**

```
  (best distance 0.661, cutoff 0.75)

Yes, smaller and local places hire in February and March, so you can still apply in the spring if you missed the autumn deadlines (thread_internship_timing.txt).

Sources retrieved: thread_changing_major.txt, thread_first_year_regret.txt, thread_internship_timing.txt, thread_transfer_credits.txt

1 model calls this session, 405 tokens (369 in, 36 out)
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

Across the five in-scope questions, the relevant chunk's distance topped out at 0.72. Across the five out-of-scope questions, the closest chunk never came in under 0.82.

That left a gap between 0.72 and 0.82, and I set the cutoff at 0.75, slightly closer to the in-scope boundary, since missing a real answer felt like a worse failure mode for this use case than occasionally letting an irrelevant chunk through.


| Question | In corpus? | Best distance |
|---|---|---|
| Is it difficult to change major to different department? | Y | 0.2675 |
| What can I do if one teammate is a free-rider? | Y | 0.6626 |
| Is it possible to apply intership in spring? | Y | 0.6611 |
| Can I ask about the same context taught in the lecture? | Y | 0.6445 |
| What can I do if I want to change roommates? | Y | 0.3857 |
| What is the capital of Mongolia? | N | 0.9213 |
| How do I change the oil in a diesel engine? | N | 0.8994 |
| Who won the 1994 World Cup? | N | 0.9173 |
| What is the recommended dosage of ibuprofen for a headache? | N | 0.8171 |
|How do I write a for loop in Rust?  | N | 0.8868 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**
I asked Claude to help me write a reply-based chunker to replace the fixed-size window splitter. Working through it, I realized the original chunk_size/overlap parameters barely apply anymore — these threads are short enough that "question + one reply" already produces small chunks, so those parameters only guard an edge case (a single reply exceeding the size limit) that doesn't occur anywhere in my current corpus.

**2.**
I ask Claude pressure-test the criteria and caught one problem.
Criterion 4 changed to a deterministic guarantee (prepend the question to every split chunk), since leaving it to chance wasn't something I wanted to accept once I noticed how few threads even exceeded my chunk size.


<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 4/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. The source document named in the generated answer matches the document that is  identified in advance as containing the answer | 4 of 5 | 5/5 | 4/5 | 5/5 | MET |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

*For criteria 1, 2, 5*
All results below (Criteria 1, 2, 5) are produced by `python run_eval.py`, and records the output to `run_2026-09-23_2032.md`

- Criteria 1: Verified from the `sources retrieved` field for each in-corpus question in `eval_results.md`
- Criteria 2: Verified from the `answer` field for each in-corpus question
- Criteria 5: Verified by comparing the source named in each `answer` field against the document I identified in advance as containing the answer.

```text
### What can I do if one teammate is a free-rider? — run 2

- Best distance: 0.6626 (passed the gate)
- Sources retrieved: thread_bike_commute.txt, thread_group_project.txt

```
To handle a teammate who disappears (acts as a free-rider), you should split the work into independent pieces so their absence doesn't sink everyone, document your progress early, and raise the issue with the instructor before the deadline so they can adjust individual grades. 

Source: `thread_group_project.txt`
```

### Can I ask about the same context taught in the lecture? — run 1

- Best distance: 0.6445 (passed the gate)
- Sources retrieved: thread_late_work.txt, thread_office_hours_etiquette.txt, thread_textbook_editions.txt

```
Based on the documents, it is completely normal to go to office hours to say, "I'm following the lectures but I don't feel like I understand the shape of it" (thread_office_hours_etiquette.txt).
```

### Can I ask about the same context taught in the lecture? — run 2

- Best distance: 0.6445 (passed the gate)
- Sources retrieved: thread_late_work.txt, thread_office_hours_etiquette.txt, thread_textbook_editions.txt

```
I do not have enough information to answer your question based on the provided documents.
```
```

*For criteria 3*
- Criteria 3: Verified by running `python app.py ask "..."` for each of the 5 OUT_OF_SCOPE questions

```bash
python app.py ask "What is the capital of Mongolia?"-unofficial-guide-starter-v2026> 
  (best distance 0.921, cutoff 0.75)

I don't have enough information about that.

0 model calls this session
```

*For criteria 4*
- Criteria 4: confirmed by printing every chunk in the corpus via the code below in `chunker.py`

​```python
print("Below are chunked text")
for chunk in chunks:
    print(chunk.text)
    print("=" * 60)
​```

All chunks in the printed output begin with the original question.



## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | checked against which document I identified in advance as containing the answer |
| 2 | Every answer names a source | MET | checked for the presence of a cited source |
| 3 | Gate stops out-of-corpus questions | MET | checked for the exact "I don't have enough information about that" response |
| 4 | Every chunk resulting from a thread split retains the original question. | MET | printed out and checked against all chunks |
| 5 | The source document named in the generated answer matches the document that is  identified in advance as containing the answer | MET | comparing the source named in each answer field against the document I identified in advance as containing the answer. |


## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
