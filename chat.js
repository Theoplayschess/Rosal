// Cloudflare Pages Function: POST /api/chat
// Uses Workers AI (free tier) through the "AI" binding, so no API key is needed.

const MODEL = "@cf/meta/llama-3.1-8b-instruct"; // swap for any chat model in the Workers AI catalog

const SYSTEM_PROMPT =
  "You are Rosal AI, a friendly and concise AI assistant. " +
  "Answer clearly, use short paragraphs, and say so when you are unsure. " +
  "Reply in the same language the user writes in.";

const MAX_MESSAGES = 20; // keep only the most recent turns to save free quota
const MAX_CHARS = 4000; // per message

export async function onRequestPost({ request, env }) {
  if (!env.AI) {
    return json({ error: "AI binding missing. Add a Workers AI binding named AI in your Pages project settings." }, 500);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Invalid JSON" }, 400);
  }

  const history = Array.isArray(body.messages) ? body.messages : [];
  const messages = history
    .filter((m) => m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
    .slice(-MAX_MESSAGES)
    .map((m) => ({ role: m.role, content: m.content.slice(0, MAX_CHARS) }));

  if (!messages.length || messages[messages.length - 1].role !== "user") {
    return json({ error: "Send at least one user message" }, 400);
  }

  try {
    const stream = await env.AI.run(MODEL, {
      messages: [{ role: "system", content: SYSTEM_PROMPT }, ...messages],
      stream: true,
      max_tokens: 700,
    });
    return new Response(stream, {
      headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
    });
  } catch (err) {
    return json({ error: "The model is unavailable right now (the daily free quota may be used up)." }, 503);
  }
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
