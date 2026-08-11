in this section, 
the goal is that, a person uploads their resume, and the system reads and understands it,
updates the format to make it ATS friendly and updates the content of the resume using an llm,
to emphasise the important points and rewriting the resume to make it look more impressive 

the system then formats this and converts it into a pdf and a download link is made available to the user 


okay now this is the system breakdown 

Step 1: Design the ATS-Optimized HTML/CSS Template


Step 2: The Pydantic-Enforced LLM Rewriter : here we use an llm to first read and then rewrite the users resume 
STAR Method Enforcement:Action + Metric + Result
The Bracket Strategy: If the LLM determines a bullet needs a quantifiable metric to sound impressive but cannot invent one,
it will insert bold brackets like [Insert % Improvement]. This forces the user to actively think about their impact.

Jargon Standardization: It will elevate the vocabulary to match high-tier engineering standards
 (e.g., emphasizing terms like "quantization," "edge deployments," and "inference latency").


 Step 3: The Data Merger (JSON to Jinja2)
Once the LLM returns the enhanced JSON, we map it dynamically into the HTML template.

We will use the Python Jinja2 templating engine.

It will loop through the experience array and automatically generate the exact number of HTML blocks needed,
ensuring perfect vertical spacing regardless of how much text the LLM generated.

Step 4: The WeasyPrint PDF Compiler
The backend will take the hydrated HTML string and pass it to WeasyPrint.

Step 5: The API Delivery
The FastAPI endpoint will return the generated PDF as a downloadable binary blob (or a base64 encoded string) directly to the Next.js frontend, 
resulting in a seamless "Click -> Download" user experience.