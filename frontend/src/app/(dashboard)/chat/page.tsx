"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { resumeService } from "@/services/resume";
import ReactMarkdown from "react-markdown";

interface Msg { role: "user" | "assistant"; content: string }

export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const { data: resumes } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => resumeService.list(),
  });
  const latestResumeId = resumes?.[0]?.id;

  async function send() {
    if (!input.trim()) return;
    const userMsg = input;
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setInput("");
    setBusy(true);
    try {
      const { data } = await api.post("/chat", {
        session_id: sessionId,
        message: userMsg,
        resume_id: latestResumeId ?? null,
      });
      setSessionId(data.session_id);
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-on-surface">AI Career Advisor</h1>
        <p className="text-on-surface-variant">
          Conversational guidance — context preserved across the session.
          {latestResumeId && (
            <span className="ml-2 text-xs text-primary font-medium">Resume connected</span>
          )}
        </p>
      </header>
      <Card className="flex h-[60vh] flex-col p-4">
        <div className="flex-1 space-y-3 overflow-auto">
          {messages.length === 0 && (
            <div className="text-sm text-on-surface-variant">
              Ask anything — &quot;How do I pivot from ML research to MLE?&quot;, &quot;What should I add to my resume?&quot;…
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                  m.role === "user"
                    ? "bg-primary text-white"
                    : "bg-surface-variant text-on-surface-variant"
                }`}
              >
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          {busy && (
            <div className="flex justify-start">
              <div className="rounded-2xl bg-surface-variant px-4 py-3 text-sm text-on-surface-variant">
                Thinking…
              </div>
            </div>
          )}
        </div>
        <div className="mt-3 flex gap-2">
          <Input
            placeholder="Type a message…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <Button onClick={send} loading={busy}>Send</Button>
        </div>
      </Card>
    </div>
  );
}
