DSE is a Diagnostic Scoring Engine,
the reason i decided to build this out is because our smart resume just rewrites any given resume,
it lacks the ability to actually judge if a resume and analyze all aspects of it,
for this reason i decided to build this DSE that helps analyze a resume and figure if its worth rewriting 


for this to work well we have defined 5 parameters that the system looks at in a resume 

The 5 Independent Evaluation Parameters
1. Structural Health & Parsability (The "ATS Format" Score)-> this checks how ats friendly the resume template is basically,
the idea on how to score it 
How it calculates (Python): We use the spatial coordinates (x0, y0) from your TextExtraction layer. 
If the variance in x0 coordinates is too high (indicating a 2-column Canva template), 
the score drops. If standard headers ("Experience", "Education") aren't found via Regex, it drops further.

2. Metric Density (The "Impact" Score) -> this is in regards to the STAR format, 
here we try and look for the candidate proving their impact with numbers, not just listing duties...


3. Linguistic Vigor -> Does the candidate sound confident? Are they using active or passive voice?

4. Semantic Depth -> Did the candidate just list "Python" in their skills section, or did they actually explain how they used Python in their projects?


5.Brevity & Conciseness -> Are the bullets too short (lacking detail) or too long (a wall of text)?
Redundancy: Are they using 15 words to say what could be said in 3? (e.g., "was responsible for the development and implementation of" vs "engineered").
Structural Pacing: Is it a single, breathless run-on sentence, or does it follow a clean, logical flow (Action -> Context -> Result)?


now some of these parameters need to be evaluated deterministically and some require and llm call,
and the final ouptut must also be an llm generated report the end use can read,

to make type of system efficient we use  The Optimized "Single-Pass" Architecture

1. Phase 1: The Deterministic Pre-Compute (Pure Python)
As soon as the user uploads their PDF, our Python engine immediately scans the spatial coordinates. 
It checks the variance of the x0 and y0 data
Output: It generates a raw score and a plain-text reason. (e.g., Score: 90/100. 
Reason: Clean, single-column layout detected with standard left-aligned indentations.)


2. Phase 2: The Unified LLM Prompt
Instead of just sending the parsed text, we inject the result of Phase 1 directly into the LLM prompt as context.  
We pass the LLM the parsed resume JSON.We explicitly tell the LLM: "The system has already evaluated the Structural Health of this resume. 
The score is 90/100 because it has a clean single-column layout. Do not recalculate this. Simply incorporate this into your final report."



3. Phase 3: The Unified LLM Output (The Master Scorecard)
Because the LLM now has both the structural context (from our math) and the semantic context (from reading the text), 
it can evaluate the remaining 4 pillars and synthesize a holistic report in one shot.



we need to talk about this one Deterministic function,
calculate_structural_health, this is used to find how well formatted the resume is,
does it have multiple columns and tables or is it ATS friendly? 

first we decided to use Standard Deviation of all the x0 coordinates,
but that failed,
The Idea: We assumed that in a single-column resume, 
all the text is neatly stacked on the left side of the page (around $x_0 = 40$ to $60$). 
Therefore, if we calculated the Standard Deviation (which measures how far apart a set of numbers are from their average), 
a single-column resume would have a very low score. A two-column resume would have half its text at $x_0 = 50$ and the other half at $x_0 = 350$, resulting in a massive spread and a high standard deviation score.



Why it Failed: Standard deviation is highly sensitive to outliers.
When we ran your resume through this math, 
it looked at these coordinates:  Most of your text starts at x0: 42.75.  
Your bullet points start at x0: 57.75.  
The Outlier: Your graduation date ("2024 – 2028") is right-aligned on the page at x0: 495.10.  
Because standard deviation squares the distance of every point from the average, that single right-aligned date pulled the entire mathematical average completely out of whack. 
The algorithm saw that number and essentially panicked, thinking: "There is text all the way at 495! This must be a massive second column!"

The Lesson: Standard deviation is "dumb" to the context of resume design. 
It aggressively punishes standard, harmless formatting like right-aligned dates or centered headers.