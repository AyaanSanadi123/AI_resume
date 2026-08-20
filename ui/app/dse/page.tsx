"use client";

import { ChangeEvent, DragEvent, useEffect, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  Check,
  FileText,
  GraduationCap,
  BriefcaseBusiness,
  RefreshCw,
  Sparkles,
  Upload,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";

/* -------------------------------------------------------------------------- */
/* Types                                                                      */
/* -------------------------------------------------------------------------- */

type ParsedResume = {
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  summary?: string;
  skills?: string[];
  experience?: Array<{
    company?: string;
    role?: string;
    title?: string;
    start_date?: string;
    end_date?: string;
    description?: string;
    bullets?: string[];
  }>;
  projects?: Array<{
    name?: string;
    description?: string;
    [key: string]: any;
  }>;
  education?: Array<{
    institution?: string;
    degree?: string;
    field?: string;
    start_date?: string;
    end_date?: string;
  }>;
  [key: string]: any;
};

type Scorecard = {
  executive_verdict?: string;
  linguistic_vigor?: { score: number; feedback: string; status?: string };
  metric_density?: { score: number; feedback: string; status?: string };
  readability?: { score: number; feedback: string; status?: string };
  semantic_depth?: { score: number; feedback: string; status?: string };
  structural_health?: { score: number; feedback: string; status?: string };
  overall_score?: number;
  [key: string]: any;
};

type AuditResponse = {
  parsed_resume: ParsedResume;
  scorecard: Scorecard;
};

type AuditStep = {
  title: string;
  description: string;
};

const AUDIT_STEPS: AuditStep[] = [
  {
    title: "Extracting raw document text...",
    description: "Reading the contents of your PDF.",
  },
  {
    title: "Structuring layout and chronological data...",
    description: "Mapping sections, dates and document structure.",
  },
  {
    title: "Running diagnostic audit...",
    description: "Evaluating clarity, impact and resume quality.",
  },
  {
    title: "Generating final scorecard...",
    description: "Turning the analysis into actionable feedback.",
  },
];

/* -------------------------------------------------------------------------- */
/* Main                                                                       */
/* -------------------------------------------------------------------------- */

export default function DSEPage() {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [stage, setStage] = useState<"upload" | "auditing" | "dashboard" | "upgrading">("upload");
  const [auditStep, setAuditStep] = useState(0);
  const [auditData, setAuditData] = useState<AuditResponse | null>(null);
  const [error, setError] = useState("");
  const [downloaded, setDownloaded] = useState(false);

  useEffect(() => {
    if (!file) return;
    runAudit(file);
  }, [file]);

  const validateFile = (selectedFile: File) => {
    if (selectedFile.type !== "application/pdf") {
      setError("Only PDF resumes are supported.");
      return false;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("Your resume must be smaller than 10 MB.");
      return false;
    }
    setError("");
    return true;
  };

  const handleFile = (selectedFile: File) => {
    if (!validateFile(selectedFile)) return;
    setDownloaded(false);
    setFile(selectedFile);
  };

  const handleInput = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) handleFile(selectedFile);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragActive(false);
    const selectedFile = event.dataTransfer.files?.[0];
    if (selectedFile) handleFile(selectedFile);
  };

  async function runAudit(resume: File) {
    setStage("auditing");
    setAuditStep(0);
    setError("");

    const progressInterval = setInterval(() => {
      setAuditStep((previous) => Math.min(previous + 1, AUDIT_STEPS.length - 1));
    }, 1800);

    try {
      const formData = new FormData();
      formData.append("file", resume);

      const response = await fetch("http://localhost:8000/api/dse/audit", {
        method: "POST",
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.message || "Unable to audit your resume.");
      }

      const data: AuditResponse = await response.json();
      console.log("DSE Backend Payload:", data);
      
      setAuditStep(AUDIT_STEPS.length - 1);
      setAuditData(data);

      setTimeout(() => {
        setStage("dashboard");
      }, 450);
    } catch (err) {
      clearInterval(progressInterval);
      setStage("upload");
      setError(err instanceof Error ? err.message : "Something went wrong while auditing your resume.");
    }
  }

  async function upgradeResume() {
    if (!auditData) return;
    setStage("upgrading");
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/dse/upgrade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          parsed_resume: auditData.parsed_resume,
          scorecard: auditData.scorecard,
        }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.message || "Unable to generate your upgraded resume.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");

      anchor.href = url;
      anchor.download = "SmartResume-Updated.pdf";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);

      setDownloaded(true);
      setStage("dashboard");
    } catch (err) {
      setStage("dashboard");
      setError(err instanceof Error ? err.message : "Something went wrong while generating your resume.");
    }
  }

  const reset = () => {
    setFile(null);
    setAuditData(null);
    setAuditStep(0);
    setDownloaded(false);
    setError("");
    setStage("upload");
  };

  /* ---------------------------------------------------------------------- */
  /* Views                                                                  */
  /* ---------------------------------------------------------------------- */

  if (stage === "upload") {
    return (
      <main className="min-h-screen bg-background">
        <Header />
        <section className="mx-auto flex min-h-[calc(100vh-65px)] w-full max-w-3xl flex-col justify-center px-6 py-16">
          <div className="mb-10 text-center">
            <Badge variant="secondary" className="mb-4">
              <Sparkles className="mr-1 size-3" />
              SmartResume Diagnostic Engine
            </Badge>
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              Understand your resume.
            </h1>
            <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground">
              Upload your current resume and let the Diagnostic Scorecard Engine identify what is working, what isn't, and what should change.
            </p>
          </div>

          <Card>
            <CardContent className="p-4 sm:p-6">
              <div
                onDragOver={(event) => {
                  event.preventDefault();
                  setDragActive(true);
                }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                className={`
                  relative flex min-h-95 flex-col items-center justify-center
                  rounded-lg border border-dashed transition-colors
                  ${dragActive ? "border-primary bg-accent" : "hover:bg-muted/40"}
                `}
              >
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleInput}
                  className="absolute inset-0 cursor-pointer opacity-0"
                />
                <div
                  className={`
                    mb-5 flex size-14 items-center justify-center
                    rounded-xl border bg-muted transition-transform
                    ${dragActive ? "scale-105" : ""}
                  `}
                >
                  <Upload className="size-6 text-muted-foreground" />
                </div>
                <h2 className="text-base font-medium">Drop your resume here</h2>
                <p className="mt-1.5 text-sm text-muted-foreground">or click anywhere to browse</p>
                <div className="mt-5 flex items-center gap-2">
                  <Badge variant="outline">PDF</Badge>
                  <span className="text-xs text-muted-foreground">Maximum 10 MB</span>
                </div>
              </div>

              {error && (
                <Alert variant="destructive" className="mt-4">
                  <AlertCircle className="size-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          <div className="mt-5 flex justify-center gap-6 text-xs text-muted-foreground">
            <span>Automatic audit</span>
            <span>•</span>
            <span>No job description required</span>
            <span>•</span>
            <span>PDF only</span>
          </div>
        </section>
      </main>
    );
  }

  if (stage === "auditing") return <AuditLoading file={file} currentStep={auditStep} />;
  if (stage === "upgrading") return <UpgradeLoading />;
  if (!auditData) return null;

  return (
    <Dashboard
      file={file}
      data={auditData}
      downloaded={downloaded}
      error={error}
      onUpgrade={upgradeResume}
      onReset={reset}
    />
  );
}

/* ========================================================================== */
/* Header                                                                     */
/* ========================================================================== */

function Header() {
  return (
    <header className="border-b">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <div className="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <FileText className="size-4" />
          </div>
          <span className="font-semibold tracking-tight">SmartResume</span>
        </div>
        <Badge variant="outline">DSE</Badge>
      </div>
    </header>
  );
}

/* ========================================================================== */
/* Audit Loading                                                              */
/* ========================================================================== */

function AuditLoading({ file, currentStep }: { file: File | null; currentStep: number }) {
  const progress = ((currentStep + 1) / AUDIT_STEPS.length) * 100;

  return (
    <main className="min-h-screen bg-background">
      <Header />
      <section className="mx-auto w-full max-w-2xl px-6 py-16">
        <div className="mb-10 text-center">
          <div className="mx-auto mb-5 flex size-12 items-center justify-center rounded-xl border bg-muted">
            <FileText className="size-5 text-muted-foreground" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">Auditing your resume</h1>
          <p className="mt-2 text-sm text-muted-foreground">{file?.name}</p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Diagnostic audit</CardTitle>
              <span className="text-xs text-muted-foreground">{Math.round(progress)}%</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <Progress value={progress} />
            <div className="space-y-5">
              {AUDIT_STEPS.map((step, index) => {
                const completed = index < currentStep;
                const active = index === currentStep;

                return (
                  <div key={step.title} className={`flex gap-3 transition-opacity ${!active && !completed ? "opacity-35" : ""}`}>
                    <div
                      className={`
                        mt-0.5 flex size-6 shrink-0 items-center justify-center
                        rounded-full border text-[10px]
                        ${completed ? "border-primary bg-primary text-primary-foreground" : active ? "border-primary" : ""}
                      `}
                    >
                      {completed ? <Check className="size-3" /> : active ? <span className="size-2 animate-pulse rounded-full bg-primary" /> : index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{step.title}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{step.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-32 rounded-xl" />
        </div>
      </section>
    </main>
  );
}

/* ========================================================================== */
/* Upgrade Loading                                                            */
/* ========================================================================== */

function UpgradeLoading() {
  return (
    <main className="min-h-screen bg-background">
      <Header />
      <section className="flex min-h-[calc(100vh-65px)] items-center justify-center px-6">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto mb-6 flex size-14 items-center justify-center rounded-xl border bg-muted">
            <RefreshCw className="size-6 animate-spin text-muted-foreground" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">Rewriting your resume</h1>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Applying the diagnostic recommendations and compiling your upgraded PDF.
          </p>
          <div className="mt-8 space-y-3 text-left">
            {["Applying content improvements", "Optimizing resume structure", "Compiling final PDF"].map((text, index) => (
              <div key={text} className="flex items-center gap-3 rounded-lg border p-3">
                <div className="flex size-6 items-center justify-center rounded-full bg-muted text-xs">{index + 1}</div>
                <span className="text-sm">{text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

/* ========================================================================== */
/* Dashboard                                                                  */
/* ========================================================================== */

function Dashboard({
  file,
  data,
  downloaded,
  error,
  onUpgrade,
  onReset,
}: {
  file: File | null;
  data: AuditResponse;
  downloaded: boolean;
  error: string;
  onUpgrade: () => void;
  onReset: () => void;
}) {
  const score = getScore(data.scorecard);
  const scoreColor = score < 50 ? "text-red-600" : score < 75 ? "text-yellow-600" : "text-green-600";
  const scoreLabel = score < 50 ? "Needs significant improvement" : score < 75 ? "Has room for improvement" : "Exceptionally strong resume";

  // Bucket the 5 pillars into UI categories
  const strengths: string[] = [];
  const weaknesses: string[] = [];
  const formatIssues: string[] = [];
  
  const sc = data.scorecard;
  const categories = [
    { name: "Linguistic Vigor", data: sc.linguistic_vigor },
    { name: "Metric Density", data: sc.metric_density },
    { name: "Readability", data: sc.readability },
    { name: "Semantic Depth", data: sc.semantic_depth },
    { name: "Structural Health", data: sc.structural_health },
  ];

  categories.forEach((cat) => {
    if (!cat.data) return;
    const feedbackText = `${cat.name} (${cat.data.score}/100): ${cat.data.feedback}`;
    if (cat.data.score >= 85) strengths.push(feedbackText);
    else if (cat.data.score < 75) weaknesses.push(feedbackText);
    else formatIssues.push(feedbackText);
  });

  return (
    <main className="min-h-screen bg-muted/20">
      <Header />
      <section className="mx-auto w-full max-w-6xl px-6 py-10">
        
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <Badge variant="secondary" className="mb-3">Diagnostic complete</Badge>
            <h1 className="text-3xl font-semibold tracking-tight">Your resume scorecard</h1>
            <p className="mt-2 text-sm text-muted-foreground">{file?.name}</p>
          </div>
          <Button variant="outline" onClick={onReset}>
            <RefreshCw className="mr-2 size-4" />
            Audit another
          </Button>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="size-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {downloaded && (
          <Alert className="mb-6 border-green-200 bg-green-50 text-green-900">
            <Check className="size-4" />
            <AlertDescription>Your upgraded resume has been downloaded successfully.</AlertDescription>
          </Alert>
        )}

        {/* Global score */}
        <Card className="mb-6">
          <CardContent className="flex flex-col items-center justify-center gap-8 p-8 sm:flex-row sm:justify-start sm:p-10">
            <ScoreRing score={score} />
            <div className="text-center sm:text-left">
              <Badge variant="outline" className="mb-3">Overall diagnostic score</Badge>
              <h2 className={`text-2xl font-semibold ${scoreColor}`}>{scoreLabel}</h2>
              <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
                <span className="font-semibold text-foreground">Executive Verdict: </span> 
                {sc.executive_verdict || "This score reflects the current quality, structure, clarity and effectiveness of your resume."}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Scorecard Bento */}
        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <InsightCard title="Strengths" count={strengths.length} items={strengths} tone="positive" />
          <InsightCard title="Critical weaknesses" count={weaknesses.length} items={weaknesses} tone="negative" />
          <InsightCard title="Room for Improvement" count={formatIssues.length} items={formatIssues} tone="warning" />
        </div>

        {/* Parsed resume verification */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div>
                <CardTitle className="text-base">What we extracted</CardTitle>
                <p className="mt-1 text-sm text-muted-foreground">
                  Verify that SmartResume correctly understood your document before rewriting it.
                </p>
              </div>
              <Badge variant="outline">Parsed resume</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <ParsedResumeView resume={data.parsed_resume} />
          </CardContent>
        </Card>

        {/* Upgrade CTA */}
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            <div className="flex flex-col gap-6 p-7 sm:flex-row sm:items-center sm:justify-between sm:p-8">
              <div>
                <Badge className="mb-3">SmartResume Upgrade</Badge>
                <h2 className="text-xl font-semibold tracking-tight">Turn this audit into a better resume.</h2>
                <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
                  SmartResume will apply the diagnostic recommendations, rewrite weak content and compile a polished PDF.
                </p>
              </div>
              <Button size="lg" onClick={onUpgrade} className="shrink-0">
                <Sparkles className="mr-2 size-4" />
                Auto-Rewrite & Upgrade
                <ArrowRight className="ml-2 size-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

/* ========================================================================== */
/* Score Ring                                                                 */
/* ========================================================================== */

function ScoreRing({ score }: { score: number }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(score, 100) / 100) * circumference;
  const color = score < 50 ? "text-red-600" : score < 75 ? "text-yellow-600" : "text-green-600";

  return (
    <div className="relative size-40 shrink-0">
      <svg className="size-full -rotate-90" viewBox="0 0 128 128">
        <circle cx="64" cy="64" r={radius} stroke="currentColor" strokeWidth="9" fill="none" className="text-muted" />
        <circle
          cx="64" cy="64" r={radius} stroke="currentColor" strokeWidth="9" fill="none"
          strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
          className={`${color} transition-all duration-1000`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-4xl font-bold tracking-tight ${color}`}>{score}</span>
        <span className="text-[10px] text-muted-foreground">/ 100</span>
      </div>
    </div>
  );
}

/* ========================================================================== */
/* Insight Card                                                               */
/* ========================================================================== */

function InsightCard({ title, count, items, tone }: { title: string; count: number; items: string[]; tone: "positive" | "negative" | "warning"; }) {
  const toneClasses = { positive: "text-green-600", negative: "text-red-600", warning: "text-yellow-600" };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">{title}</CardTitle>
          <Badge variant="secondary">{count}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-xs text-muted-foreground">Nothing reported here.</p>
        ) : (
          <ul className="space-y-3">
            {items.map((item, index) => (
              <li key={`${item}-${index}`} className="flex gap-2 text-xs leading-5 text-muted-foreground">
                <span className={`mt-2 size-1.5 shrink-0 rounded-full bg-current ${toneClasses[tone]}`} />
                {item}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

/* ========================================================================== */
/* Parsed Resume                                                              */
/* ========================================================================== */

function ParsedResumeView({ resume }: { resume: ParsedResume }) {
  const hasExpOrProjects = (resume.experience && resume.experience.length > 0) || (resume.projects && resume.projects.length > 0);

  return (
    <div className="space-y-6">
      {/* Identity */}
      <div>
        <p className="text-lg font-semibold">{resume.name || "Name not detected"}</p>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.location && <span>{resume.location}</span>}
        </div>
      </div>

      <Separator />

      {/* Summary */}
      {resume.summary && (
        <section>
          <SectionHeading title="Summary" />
          <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">{resume.summary}</p>
        </section>
      )}

      {/* Skills */}
      {resume.skills && resume.skills.length > 0 && (
        <section>
          <SectionHeading title="Skills" />
          <div className="mt-3 flex flex-wrap gap-2">
            {resume.skills.map((skill) => (
              <Badge variant="secondary" key={skill}>{skill}</Badge>
            ))}
          </div>
        </section>
      )}

      {/* Experience & Projects */}
      {hasExpOrProjects && (
        <section>
          <SectionHeading title="Experience & Projects" icon={<BriefcaseBusiness className="size-4" />} />
          <div className="mt-4 space-y-5">
            {resume.experience?.map((job, index) => (
              <div key={`exp-${index}`} className="relative border-l pl-5">
                <div className="absolute -left-[5px] top-1.5 size-2.5 rounded-full border-2 border-background bg-border" />
                <p className="text-sm font-medium">{job.role || job.title || "Role not detected"}</p>
                <p className="mt-1 text-xs text-muted-foreground">{job.company || "Company not detected"}</p>
                {(job.start_date || job.end_date) && (
                  <p className="mt-1 text-xs text-muted-foreground">{job.start_date || "—"} — {job.end_date || "Present"}</p>
                )}
              </div>
            ))}
            {resume.projects?.map((project, index) => (
              <div key={`proj-${index}`} className="relative border-l pl-5">
                <div className="absolute -left-[5px] top-1.5 size-2.5 rounded-full border-2 border-background bg-primary/50" />
                <p className="text-sm font-medium">{project.name || "Project Name not detected"}</p>
                <p className="mt-1 text-xs text-muted-foreground">Technical Project</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Education */}
      {resume.education && resume.education.length > 0 && (
        <section>
          <SectionHeading title="Education" icon={<GraduationCap className="size-4" />} />
          <div className="mt-4 space-y-4">
            {resume.education.map((education, index) => (
              <div key={index}>
                <p className="text-sm font-medium">
                  {education.degree || "Degree not detected"}
                  {education.field ? ` · ${education.field}` : ""}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">{education.institution || "Institution not detected"}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

/* ========================================================================== */
/* Helpers                                                                    */
/* ========================================================================== */

function SectionHeading({ title, icon }: { title: string; icon?: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2">
      {icon && <span className="text-muted-foreground">{icon}</span>}
      <h3 className="text-sm font-medium">{title}</h3>
    </div>
  );
}

function getScore(scorecard: Scorecard) {
  const scores = [
    scorecard.linguistic_vigor?.score,
    scorecard.metric_density?.score,
    scorecard.readability?.score,
    scorecard.semantic_depth?.score,
    scorecard.structural_health?.score,
  ].filter((s) => typeof s === "number") as number[];

  if (scores.length === 0) return 0;
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
  return Math.max(0, Math.min(100, Math.round(avg)));
}