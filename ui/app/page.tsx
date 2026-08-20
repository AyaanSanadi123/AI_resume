"use client";

import Link from "next/link";
import { useTheme } from "next-themes";
import { 
  ArrowRight, 
  BrainCircuit, 
  Code2, 
  FileText, 
  Headphones, 
  Moon, 
  Sun 
} from "lucide-react";
import { FaGithub } from "react-icons/fa";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Dashboard() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch for theme toggle
  useEffect(() => setMounted(true), []);

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      {/* --- NAVBAR --- */}
      <nav className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-lg">
              <BrainCircuit className="size-5"/>
            </div>
            <span className="text-lg font-bold tracking-tight">SmartResume AI</span>
          </div>
          
          <div className="flex items-center gap-4">
            <Link href="https://github.com/AyaanSanadi123" target="_blank">
              <Button size="icon" variant="ghost">
                <FaGithub className="size-5"/>
              </Button>
            </Link>
            {mounted && (
              <Button 
                size="icon" 
                variant="ghost" 
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              >
                {theme === "dark" ? <Sun className="size-5"/> : <Moon className="size-5"/>}
              </Button>
            )}
          </div>
        </div>
      </nav>

      {/* --- HERO SECTION --- */}
      <main className="mx-auto max-w-7xl px-6 py-20 sm:py-32">
        <div className="text-center">
          <Badge className="mb-6 px-4 py-1.5 text-sm" variant="secondary">
            <span className="flex items-center gap-2">
              <span className="relative flex size-2">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex size-2 rounded-full bg-green-500"></span>
              </span>
              v1.0 Engines Online
            </span>
          </Badge>
          
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-7xl">
            Real-Time AI <br className="hidden sm:block" />
            <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              Mock Interviews.
            </span>
          </h1>
          
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
            A full-stack voice agent architecture built to test engineering candidates. 
            Upload a resume, bypass the ATS, and engage in a zero-latency WebRTC conversation with an AI tuned to your exact background.
          </p>
          
          {/* --- ROUTING ENGINE BUTTONS --- */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link href="/interview">
              <Button className="h-12 px-8 text-base shadow-xl" size="lg">
                <Headphones className="mr-2 size-5"/>
                Mock Interview
              </Button>
            </Link>
            
            <Link href="/ats">
              <Button className="h-12 px-8 text-base shadow-sm" size="lg" variant="secondary">
                <FileText className="mr-2 size-5"/>
                ATS Scanner
              </Button>
            </Link>

            <Link href="/dse">
              <Button className="h-12 px-8 text-base shadow-sm" size="lg" variant="secondary">
                <Code2 className="mr-2 size-5"/>
                DSE Engine
              </Button>
            </Link>
          </div>

          <div className="mt-8">
            <Link href="#architecture">
              <Button className="text-muted-foreground" size="sm" variant="ghost">
                View Architecture <ArrowRight className="ml-2 size-4"/>
              </Button>
            </Link>
          </div>
        </div>

        {/* --- ARCHITECTURE GRID --- */}
        <div id="architecture" className="mt-32">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold tracking-tight">How it works under the hood</h2>
            <p className="mt-2 text-muted-foreground">The technical pipeline powering the voice agent.</p>
          </div>
          
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="bg-card transition-all hover:shadow-md">
              <CardHeader>
                <FileText className="mb-2 size-8 text-blue-500"/>
                <CardTitle>1. ATS Text Extraction</CardTitle>
                <CardDescription>Python FastAPI & Resume Parsing</CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                We utilize PyMuPDF and NLP to extract raw text from candidate resumes, categorizing skills and experience into a clean JSON schema before the interview begins.
              </CardContent>
            </Card>

            <Card className="bg-card transition-all hover:shadow-md">
              <CardHeader>
                <Code2 className="mb-2 size-8 text-purple-500"/>
                <CardTitle>2. Dynamic Context Caching</CardTitle>
                <CardDescription>Gemini Caching API & Prompt Tuning</CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                To eliminate latency and bypass token limits, candidate data and scraped GitHub profiles are pre-loaded into a dedicated LLM cache spanning the life of the session.
              </CardContent>
            </Card>

            <Card className="bg-card transition-all hover:shadow-md">
              <CardHeader>
                <Headphones className="mb-2 size-8 text-green-500"/>
                <CardTitle>3. WebRTC Voice Pipeline</CardTitle>
                <CardDescription>Pipecat, Deepgram & Silero VAD</CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                The frontend streams raw audio via `aiortc` to our backend transport. We employ Silero Voice Activity Detection and Deepgram STT for sub-second conversational turn-taking.
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* --- FOOTER --- */}
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        <p>Built by Ayaan Sanadi 1BY24AI024. Powered by Next.js, FastAPI, and Pipecat.</p>
      </footer>
    </div>
  );
}