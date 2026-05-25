"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import ReactMarkdown from "react-markdown";

interface Msg { role: "user" | "assistant"; content: string }

export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!input.trim()) return;
    const userMsg = input;
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setInput("");
    setBusy(true);
    try {
      const { data } = await api.post("/chat", { session_id: sessionId, message: userMsg });
      setSessionId(data.session_id);
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">AI Career Advisor</h1>
        <p className="text-slate-400">Conversational guidance — context preserved across the session.</p>
      </header>
      <Card className="flex h-[60vh] flex-col">
        <div className="flex-1 space-y-3 overflow-auto p-4">
          {messages.length === 0 && (
            <div className="text-sm text-slate-500">Ask anything — "How do I pivot from ML research to MLE?", "What should I add to my resume?"…</div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${m.role === "user" ? "bg-brand-500 text-white" : "bg-white/5 text-slate-100"}`}>
                <div className="prose prose-sm prose-invert max-w-none">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
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
