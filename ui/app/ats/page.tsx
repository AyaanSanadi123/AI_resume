"use client";

import { ChangeEvent, DragEvent, useState, useEffect } from "react";
import {
  ArrowRight,
  Check,
  FileText,
  Lock,
  Upload,
  X,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";

const steps = [
  {
    title: "Extracting resume content",
    description: "Reading your experience, skills and projects.",
  },
  {
    title: "Understanding target role",
    description: "Identifying the skills required for the position.",
  },
  {
    title: "Running semantic match",
    description: "Comparing your resume against the role.",
  },
  {
    title: "Finding ATS gaps",
    description: "Identifying missing keywords and weak areas.",
  },
  {
    title: "Generating recommendations",
    description: "Preparing actionable improvements.",
  },
];

const popularRoles = [
  "AI / ML Engineer",
  "Software Engineer",
  "Data Scientist",
  "Full Stack Developer",
];

export default function ATSPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobRole, setJobRole] = useState("");
  const [availableRoles, setAvailableRoles] = useState<string[]>([]);
  const [isLoadingRoles, setIsLoadingRoles] = useState(true);

  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const [analysisResult, setAnalysisResult] = useState<any>(null);

  // Fetch job roles from FastAPI on mount
  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/ats/roles");
        if (response.ok) {
          const data = await response.json();
          setAvailableRoles(data.roles || []);
        } else {
          console.error("Failed to load roles from backend.");
        }
      } catch (err) {
        console.error("Network error while fetching roles:", err);
      } finally {
        setIsLoadingRoles(false);
      }
    };

    fetchRoles();
  }, []);

  const resetAnalysis = () => {
    setFile(null);
    setJobRole("");
    setAnalysisResult(null);
    setCurrentStep(0);
  };

  const validateFile = (file: File) => {
    setError("");

    if (file.type !== "application/pdf") {
      setError("Please upload a PDF file.");
      return false;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("Your resume must be smaller than 10 MB.");
      return false;
    }

    return true;
  };

  const handleFile = (file: File) => {
    if (!validateFile(file)) return;

    setFile(file);
  };

  const handleFileInput = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (file) {
      handleFile(file);
    }
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragActive(false);

    const file = event.dataTransfer.files?.[0];

    if (file) {
      handleFile(file);
    }
  };

  const analyzeResume = async () => {
    if (!file || !jobRole.trim()) return;

    setError("");
    setIsAnalyzing(true);
    setCurrentStep(0);

    const formData = new FormData();

    // Field names match FastAPI endpoint requirements: file and target_role
    formData.append("file", file);
    formData.append("target_role", jobRole.trim());

    let step = 0;

    const interval = setInterval(() => {
      step++;

      if (step < steps.length) {
        setCurrentStep(step);
      }
    }, 1800);

    try {
      const response = await fetch("http://localhost:8000/api/ats/analyze", {
        method: "POST",
        body: formData,
      });

      clearInterval(interval);

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || "Unable to analyze your resume.");
      }

      const result = await response.json();
      console.log("Analysis Result:", result);

      setCurrentStep(steps.length - 1);

      setTimeout(() => {
        setAnalysisResult(result);
        setIsAnalyzing(false);
      }, 1000);
    } catch (error) {
      clearInterval(interval);

      setIsAnalyzing(false);

      setError(
        error instanceof Error ? error.message : "Something went wrong."
      );
    }
  };

  /*
   * ANALYSIS SCREEN (LOADING)
   */
  if (isAnalyzing) {
    const progress = ((currentStep + 1) / steps.length) * 100;

    return (
      <main className="min-h-screen bg-background">
        <div className="mx-auto flex min-h-screen w-full max-w-2xl flex-col justify-center px-6 py-16">
          {/* Header */}
          <div className="mb-10 text-center">
            <div className="mx-auto mb-5 flex size-12 items-center justify-center rounded-xl border bg-muted">
              <Spinner className="size-5" />
            </div>

            <h1 className="text-2xl font-semibold tracking-tight">
              Analyzing your resume
            </h1>

            <p className="mt-2 text-sm text-muted-foreground">
              Comparing your resume with{" "}
              <span className="font-medium text-foreground">{jobRole}</span>
            </p>
          </div>

          {/* Progress */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Analysis progress</CardTitle>
              <CardDescription>
                This usually takes a few seconds.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              <Progress value={progress} />

              <div className="space-y-5">
                {steps.map((step, index) => {
                  const completed = index < currentStep;
                  const active = index === currentStep;

                  return (
                    <div key={step.title} className="flex items-start gap-3">
                      <div
                        className={`
                          mt-0.5 flex size-6 shrink-0
                          items-center justify-center
                          rounded-full border
                          text-xs
                          ${
                            completed
                              ? "border-primary bg-primary text-primary-foreground"
                              : active
                                ? "border-primary"
                                : "text-muted-foreground"
                          }
                        `}
                      >
                        {completed ? (
                          <Check className="size-3.5" />
                        ) : active ? (
                          <Spinner className="size-3" />
                        ) : (
                          index + 1
                        )}
                      </div>

                      <div>
                        <p
                          className={`text-sm font-medium ${
                            !active && !completed ? "text-muted-foreground" : ""
                          }`}
                        >
                          {step.title}
                        </p>

                        <p className="mt-0.5 text-xs text-muted-foreground">
                          {step.description}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Skeleton result preview */}
          <div className="mt-4 grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <Skeleton className="h-4 w-24" />
              </CardHeader>

              <CardContent>
                <Skeleton className="h-10 w-20" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Skeleton className="h-4 w-28" />
              </CardHeader>

              <CardContent className="space-y-2">
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-3/4" />
              </CardContent>
            </Card>
          </div>

          <div className="mt-6 flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <Lock className="size-3" />
            Your resume is processed securely.
          </div>
        </div>
      </main>
    );
  }

  /*
   * RESULTS SCREEN (DASHBOARD)
   */
  if (analysisResult) {
    // Destructure using safe fallbacks in case your backend sends slightly different keys
    const { match_data, advice, parsed_data } = analysisResult;
    
    // Safely extract the score (adjust the property name if your backend uses match_score instead of score)
    const matchScore = match_data?.score || match_data?.match_score || 0;

    return (
      <main className="min-h-screen bg-background px-6 py-16">
        <div className="mx-auto w-full max-w-5xl space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between border-b pb-6">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Analysis Complete</h1>
              <p className="mt-2 text-muted-foreground">
                Target Role:{" "}
                <span className="font-semibold text-foreground">{jobRole}</span>
              </p>
            </div>
            <Button variant="outline" onClick={resetAnalysis}>
              Analyze Another Resume
            </Button>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {/* Left Column: Match Score */}
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>Match Score</CardTitle>
                <CardDescription>Based on semantic similarity</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center py-8">
                <div className="flex size-40 items-center justify-center rounded-full border-8 border-primary/20 bg-primary/5">
                  <span className="text-5xl font-bold text-primary">
                    {typeof matchScore === "number" ? Math.round(matchScore) : matchScore}%
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Right Column: AI Recommendations */}
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>AI Recommendations</CardTitle>
                <CardDescription>Actionable steps to improve your resume</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 overflow-y-auto space-y-4 rounded-lg bg-muted p-5 text-sm leading-relaxed">
                  {advice ? (
                    <>
                      {advice.reality_check && (
                        <div>
                          <span className="font-semibold text-primary">Reality Check:</span>
                          <p className="mt-1 text-muted-foreground">{advice.reality_check}</p>
                        </div>
                      )}
                      
                      {advice.skill_advice && (
                        <div>
                          <span className="font-semibold text-primary">Skill Gaps:</span>
                          <p className="mt-1 text-muted-foreground">{advice.skill_advice}</p>
                        </div>
                      )}
                      
                      {advice.impact_advice && (
                        <div>
                          <span className="font-semibold text-primary">Impact & Metrics:</span>
                          <p className="mt-1 text-muted-foreground">{advice.impact_advice}</p>
                        </div>
                      )}
                      
                      {advice.trajectory_advice && (
                        <div>
                          <span className="font-semibold text-primary">Career Trajectory:</span>
                          <p className="mt-1 text-muted-foreground">{advice.trajectory_advice}</p>
                        </div>
                      )}
                    </>
                  ) : (
                    "No specific advice generated by the LLM Advisor."
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Bottom Row: Parsed Info Check */}
          <Card>
            <CardHeader>
              <CardTitle>Parsed Data Preview</CardTitle>
              <CardDescription>
                What the ATS actually extracted from your PDF
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="mb-2 text-sm font-semibold">Detected Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {parsed_data?.skills && parsed_data.skills.length > 0 ? (
                      parsed_data.skills.map((skill: string, i: number) => (
                        <Badge key={i} variant="secondary">
                          {skill}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-muted-foreground">
                        No skills detected.
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    );
  }

  /*
   * UPLOAD SCREEN
   */
  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <FileText className="size-4" />
            </div>

            <span className="font-semibold tracking-tight">SmartResume</span>
          </div>

          <Badge variant="secondary">AI Resume Analysis</Badge>
        </div>
      </header>

      {/* Main */}
      <section className="mx-auto w-full max-w-2xl px-6 py-16">
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Resume ATS Analyzer
          </h1>

          <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-muted-foreground">
            See how well your resume matches your target role and discover
            exactly what you can improve.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Analyze your resume</CardTitle>

            <CardDescription>
              Upload your resume and select the role you're targeting.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-7">
            {/* Upload Section */}
            <div className="space-y-3">
              <Label>Resume</Label>

              {!file ? (
                <div
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragActive(true);
                  }}
                  onDragLeave={() => setDragActive(false)}
                  onDrop={handleDrop}
                  className={`
                    relative flex min-h-55
                    cursor-pointer flex-col
                    items-center justify-center
                    rounded-lg border border-dashed
                    transition-colors
                    ${
                      dragActive
                        ? "border-primary bg-accent"
                        : "hover:bg-muted/50"
                    }
                  `}
                >
                  <input
                    id="resume"
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileInput}
                    className="absolute inset-0 cursor-pointer opacity-0"
                  />

                  <div className="mb-4 flex size-11 items-center justify-center rounded-lg border bg-muted">
                    <Upload className="size-5 text-muted-foreground" />
                  </div>

                  <p className="text-sm font-medium">Drop your resume here</p>

                  <p className="mt-1 text-xs text-muted-foreground">
                    or click to browse
                  </p>

                  <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                    <Badge variant="outline">PDF</Badge>
                    <span>Maximum 10 MB</span>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3 rounded-lg border p-4">
                  <div className="flex size-10 shrink-0 items-center justify-center rounded-md bg-muted">
                    <FileText className="size-5 text-muted-foreground" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{file.name}</p>

                    <p className="mt-1 text-xs text-muted-foreground">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>

                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setFile(null)}
                  >
                    <X className="size-4" />
                  </Button>
                </div>
              )}

              {error && <p className="text-xs text-destructive">{error}</p>}
            </div>

            {/* Job Role Section */}
            <div className="space-y-3">
              <Label htmlFor="jobRole">Target job role</Label>

              {/* Styled Dropdown Selector matching Shadcn UI styling */}
              <div className="relative">
                <select
                  id="jobRole"
                  value={jobRole}
                  onChange={(e) => setJobRole(e.target.value)}
                  disabled={isLoadingRoles}
                  aria-label="Target job role"
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="" disabled>
                    {isLoadingRoles
                      ? "Loading available roles..."
                      : "Select your target role"}
                  </option>
                  {availableRoles.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </div>

              {/* Popular Role Quick Selection */}
              <div className="flex flex-wrap gap-2">
                {popularRoles.map((role) => (
                  <Button
                    key={role}
                    type="button"
                    variant={jobRole === role ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => setJobRole(role)}
                  >
                    {role}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex-col gap-3">
            <Button
              className="w-full"
              size="lg"
              disabled={!file || !jobRole.trim()}
              onClick={analyzeResume}
            >
              Analyze my resume
              <ArrowRight className="ml-2 size-4" />
            </Button>

            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Lock className="size-3" />
              Your resume is processed securely.
            </div>
          </CardFooter>
        </Card>

        {/* Bottom Benefits */}
        <div className="mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Check className="size-3 text-green-600" />
            ATS compatibility
          </span>

          <span className="flex items-center gap-1.5">
            <Check className="size-3 text-green-600" />
            Semantic matching
          </span>

          <span className="flex items-center gap-1.5">
            <Check className="size-3 text-green-600" />
            Actionable feedback
          </span>
        </div>
      </section>
    </main>
  );
}