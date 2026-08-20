"use client";

import { useEffect, useRef, useState } from "react";
import {
  AlertCircle,
  Loader2,
  Mic,
  MicOff,
  PhoneOff,
  Radio,
  AudioWaveform,
} from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

type ConnectionState = "idle" | "connecting" | "connected" | "disconnected" | "error";

export default function LiveRoom({ sessionId }: { sessionId: string }) {
  const [connectionState, setConnectionState] = useState<ConnectionState>("idle");
  const [error, setError] = useState<string>("");
  const [isMuted, setIsMuted] = useState(false);

  // References to keep WebRTC objects alive across renders
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  /* ---------------------------------------------------------------------- */
  /* WebRTC Connection Logic                                                */
  /* ---------------------------------------------------------------------- */
  const startCall = async () => {
    setConnectionState("connecting");
    setError("");

    try {
      // 1. Get Microphone Access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      localStreamRef.current = stream;

      // 2. Initialize WebRTC Peer Connection
      const pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }], // Standard public STUN
      });
      peerConnectionRef.current = pc;

      // 3. Attach Local Microphone to Peer Connection
      stream.getTracks().forEach((track) => pc.addTrack(track, stream));

      // 4. Listen for the AI's returning Audio Track
      pc.ontrack = (event) => {
        console.log("🎙️ AI Audio Track Received!");
        if (audioPlayerRef.current) {
          audioPlayerRef.current.srcObject = event.streams[0];
        }
      };

      // Handle connection drops
      pc.onconnectionstatechange = () => {
        console.log("WebRTC State:", pc.connectionState);
        if (pc.connectionState === "disconnected" || pc.connectionState === "failed") {
          endCall();
        }
      };

      // 5. Create Local Offer
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      // Wait briefly for ICE candidates to gather (Trickle ICE simplification for Python)
      await new Promise((resolve) => setTimeout(resolve, 500));

      // 6. Send Offer + Session ID to your FastAPI Signaling Endpoint
      const response = await fetch("http://localhost:8000/api/interview/offer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          sdp: pc.localDescription?.sdp,
          type: pc.localDescription?.type,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend rejected the WebRTC offer.");
      }

      // 7. Receive and Set the AI's Answer
      const answer = await response.json();
      await pc.setRemoteDescription(answer);

      setConnectionState("connected");
    } catch (err) {
      console.error("WebRTC Error:", err);
      setError(err instanceof Error ? err.message : "Failed to connect to AI.");
      endCall();
    }
  };

  /* ---------------------------------------------------------------------- */
  /* Call Controls                                                          */
  /* ---------------------------------------------------------------------- */
  const endCall = () => {
    // Stop microphone
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => track.stop());
      localStreamRef.current = null;
    }

    // Close Peer Connection
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }

    setConnectionState("disconnected");
  };

  const toggleMute = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getAudioTracks().forEach((track) => {
        track.enabled = !track.enabled;
      });
      setIsMuted(!isMuted);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => endCall();
  }, []);

  /* ---------------------------------------------------------------------- */
  /* Render UI                                                              */
  /* ---------------------------------------------------------------------- */
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-background px-6">
      {/* Hidden Audio Player for the AI's voice */}
      <audio ref={audioPlayerRef} autoPlay playsInline className="hidden" />

      <div className="w-full max-w-lg text-center">
        <Badge variant="outline" className="mb-6">
          <Radio className="mr-2 size-3 animate-pulse text-primary" />
          Session: {sessionId}
        </Badge>

        <Card className="overflow-hidden border-2 border-muted shadow-xl">
          <CardContent className="flex flex-col items-center p-12">
            
            {/* The Animated Voice Orb */}
            <div className="relative mb-8 flex size-32 items-center justify-center">
              {connectionState === "connected" && (
                <>
                  <div className="absolute size-full animate-ping rounded-full bg-primary/20" />
                  <div className="absolute size-full animate-pulse rounded-full bg-primary/40 duration-1000" />
                </>
              )}
              <div
                className={`z-10 flex size-24 items-center justify-center rounded-full transition-colors duration-500 ${
                  connectionState === "connected" ? "bg-primary text-primary-foreground" : "bg-muted"
                }`}
              >
                {connectionState === "connecting" ? (
                  <Loader2 className="size-8 animate-spin" />
                ) : (
                  <AudioWaveform className="size-10" />
                )}
              </div>
            </div>

            <h2 className="text-2xl font-bold tracking-tight">
              {connectionState === "idle" && "Ready to begin?"}
              {connectionState === "connecting" && "Connecting to AI..."}
              {connectionState === "connected" && "Interview in Progress"}
              {connectionState === "disconnected" && "Interview Concluded"}
            </h2>

            <p className="mt-2 text-sm text-muted-foreground">
              {connectionState === "idle" && "Ensure you are in a quiet environment. The AI will introduce itself once connected."}
              {connectionState === "connected" && "The AI is listening. Speak clearly into your microphone."}
              {connectionState === "disconnected" && "You can safely close this window or return to the dashboard."}
            </p>

            {error && (
              <Alert variant="destructive" className="mt-6 text-left">
                <AlertCircle className="size-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Action Buttons */}
            <div className="mt-10 flex w-full items-center justify-center gap-4">
              {connectionState === "idle" || connectionState === "disconnected" ? (
                <Button size="lg" className="w-full max-w-xs" onClick={startCall}>
                  Start Interview
                </Button>
              ) : (
                <>
                  <Button
                    size="icon"
                    variant={isMuted ? "destructive" : "secondary"}
                    className="size-14 rounded-full"
                    onClick={toggleMute}
                  >
                    {isMuted ? <MicOff className="size-6" /> : <Mic className="size-6" />}
                  </Button>
                  
                  <Button
                    size="icon"
                    variant="destructive"
                    className="size-14 rounded-full"
                    onClick={endCall}
                  >
                    <PhoneOff className="size-6" />
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}