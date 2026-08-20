"use client";

import { ChangeEvent, DragEvent, useState, useEffect } from "react";
import {
  ArrowRight,
  BriefcaseBusiness,
  FileText,
  Headphones,
  Upload,
  X,
} from "lucide-react";
import { FaGithub } from "react-icons/fa";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";

// We will build this LiveRoom component next!
import LiveRoom from "./LiveRoom"; 

export default function MockInterviewPage() {
  const [stage, setStage] = useState<"setup" | "initializing" | "live">("setup");
  
  // Form State
  const [file, setFile] = useState<File | null>(null);
  const [jobRole, setJobRole] = useState("AI/ML Engineer");
  const [githubLink, setGithubLink] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");

  // Session Data
  const [sessionId, setSessionId] = useState<string | null>(null);

  // ---> NEW: Rate Limit Cooldown State
  const [retryCountdown, setRetryCountdown] = useState<number | null>(null);

  // ---> NEW: The Countdown Timer Effect
  useEffect(() => {
    if (retryCountdown === null || retryCountdown <= 0) return;
    
    const timer = setInterval(() => {
      setRetryCountdown((prev) => {
        if (prev === null) return null;
        if (prev <= 1) {
          setError(""); // Clear the error when the timer finishes
          return null;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [retryCountdown]);

  /* ---------------------------------------------------------------------- */
  /* File Handling                                                          */
  /* ---------------------------------------------------------------------- */
  const validateFile = (selectedFile: File) => {
    if (selectedFile.type !== "application/pdf") {
      setError("Please upload your resume as a PDF.");
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
    setFile(selectedFile);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) handleFile(droppedFile);
  };

  /* ---------------------------------------------------------------------- */
  /* Initialization Pipeline                                                */
  /* ---------------------------------------------------------------------- */
  const initializeSession = async () => {
    if (!file || !jobRole.trim()) {
      setError("A resume and target role are required.");
      return;
    }

    setError("");
    setStage("initializing");

    try {
      const formData = new FormData();
      
      // Keys must match FastAPI Form(...) parameters exactly
      formData.append("resume", file);
      formData.append("target_role", jobRole.trim());
      formData.append("github_link", githubLink.trim());
      formData.append("user_id", `user_${Math.random().toString(36).substring(7)}`); // Mocking a user ID

      const response = await fetch("http://localhost:8000/api/interview/init", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const errorMessage = String(errorData?.detail || "Failed to initialize interview session.");
        
        // ---> NEW: Intercept Google's 429 Rate Limit
        if (errorMessage.includes("429") || errorMessage.includes("RESOURCE_EXHAUSTED")) {
          // Look for "retry in 31.77s" in the string
          const match = errorMessage.match(/retry in ([\d\.]+)s/i);
          const delaySeconds = match && match[1] ? Math.ceil(parseFloat(match[1])) : 60; // Fallback to 60s if not found
          
          setRetryCountdown(delaySeconds);
          throw new Error(`Google API free-tier rate limit reached. Retrying paused for ${delaySeconds} seconds.`);
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log("✅ Session Initialized:", data);
      
      setSessionId(data.session_id);
      setStage("live");
      
    } catch (err) {
      setStage("setup");
      setError(err instanceof Error ? err.message : "Something went wrong.");
    }
  };

  /* ---------------------------------------------------------------------- */
  /* Render Loading Screen                                                  */
  /* ---------------------------------------------------------------------- */
  if (stage === "initializing") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto mb-6 flex size-14 items-center justify-center rounded-xl border bg-muted">
            <Spinner className="size-6 text-primary" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">Preparing your interview room</h1>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Parsing your resume, scraping your GitHub profile, and generating the AI context cache.
          </p>
        </div>
      </main>
    );
  }

  /* ---------------------------------------------------------------------- */
  /* Render Live Room Handoff                                               */
  /* ---------------------------------------------------------------------- */
  if (stage === "live" && sessionId) {
    return <LiveRoom sessionId={sessionId} />;
  }

  /* ---------------------------------------------------------------------- */
  /* Render Setup Form                                                      */
  /* ---------------------------------------------------------------------- */
  return (
    <main className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Headphones className="size-4" />
            </div>
            <span className="font-semibold tracking-tight">SmartResume Voice AI</span>
          </div>
          <Badge variant="secondary">Live Mock Interview</Badge>
        </div>
      </header>

      <section className="mx-auto w-full max-w-2xl px-6 py-16">
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Configure your interview
          </h1>
          <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-muted-foreground">
            Provide your context so the AI can tailor the technical and behavioral questions to your exact background.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Session Context</CardTitle>
            <CardDescription>
              Upload your latest resume and optional GitHub link to begin.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Resume Upload */}
            <div className="space-y-3">
              <Label>Resume (Required)</Label>
              {!file ? (
                <div
                  onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                  onDragLeave={() => setDragActive(false)}
                  onDrop={handleDrop}
                  className={`relative flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed transition-colors ${dragActive ? "border-primary bg-accent" : "hover:bg-muted/50"}`}
                >
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                    className="absolute inset-0 cursor-pointer opacity-0"
                  />
                  <Upload className="mb-3 size-5 text-muted-foreground" />
                  <p className="text-sm font-medium">Drop your resume here</p>
                  <p className="mt-1 text-xs text-muted-foreground">PDF maximum 10 MB</p>
                </div>
              ) : (
                <div className="flex items-center gap-3 rounded-lg border p-4">
                  <div className="flex size-10 shrink-0 items-center justify-center rounded-md bg-muted">
                    <FileText className="size-5 text-muted-foreground" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{file.name}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                  <Button variant="ghost" size="icon-sm" onClick={() => setFile(null)}>
                    <X className="size-4" />
                  </Button>
                </div>
              )}
            </div>

            {/* Job Role Input */}
            <div className="space-y-3">
              <Label htmlFor="jobRole">Target Role (Required)</Label>
              <div className="relative">
                <BriefcaseBusiness className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
                <Input
                  id="jobRole"
                  value={jobRole}
                  onChange={(e) => setJobRole(e.target.value)}
                  className="pl-9"
                  placeholder="e.g. Full Stack Engineer"
                />
              </div>
            </div>

            {/* GitHub Link Input */}
            <div className="space-y-3">
              <Label htmlFor="github">GitHub Profile (Optional)</Label>
              <div className="relative">
                <FaGithub className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
                <Input
                  id="github"
                  value={githubLink}
                  onChange={(e) => setGithubLink(e.target.value)}
                  className="pl-9"
                  placeholder="https://github.com/username"
                />
              </div>
            </div>

            {error && <p className="text-sm font-medium text-destructive">{error}</p>}
          </CardContent>

          <CardFooter>
            {/* ---> NEW: Dynamic Button rendering the countdown timer */}
            <Button 
              className="w-full transition-all" 
              size="lg" 
              disabled={!file || !jobRole.trim() || retryCountdown !== null} 
              onClick={initializeSession}
            >
              {retryCountdown !== null ? (
                <>Rate Limited. Please wait {retryCountdown}s...</>
              ) : (
                <>
                  Enter Interview Room
                  <ArrowRight className="ml-2 size-4" />
                </>
              )}
            </Button>
          </CardFooter>
        </Card>
      </section>
    </main>
  );
}