# Rosal AI

A free-to-host AI chatbot. Static front end + one serverless function that talks to
Cloudflare Workers AI (no API key, no credit card needed).

```
rosal-ai/
├── index.html              chat interface (streaming replies, saved history)
├── logo.svg                your logo
├── mark.svg                logo mark without text (header + favicon)
└── functions/api/chat.js   backend: POST /api/chat -> Workers AI
```

## Free limits (read this first)

- Cloudflare Pages: free hosting on a `*.pages.dev` address, free SSL.
- Workers AI: 10,000 "Neurons" per day free, reset at 00:00 UTC. Past that, requests
  fail until the next day unless you switch to a paid plan.
  ([pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/))
  That is enough for a personal project or a small demo, not for lots of users.
- Everything is public: anyone with the URL can use your quota. See "Protect your quota".

## Option A: deploy with Git (recommended)

1. Create a free account at https://dash.cloudflare.com and a free GitHub account.
2. Create a new GitHub repository and upload the contents of this folder
   (keep the `functions` folder as is).
3. In Cloudflare: **Workers & Pages -> Create -> Pages -> Connect to Git**, pick the repo.
4. Build settings: framework preset **None**, build command empty,
   output directory `/` (or leave blank). Click **Save and Deploy**.
5. Add the AI binding: open the project -> **Settings -> Bindings -> Add -> Workers AI**.
   Set the variable name to exactly `AI`, save.
6. **Redeploy** (Deployments -> latest -> Retry deployment), because bindings only apply to
   new deployments.
7. Open `https://<your-project>.pages.dev` and chat.

## Option B: deploy from your computer with Wrangler

Dashboard drag-and-drop does NOT support the `functions` folder, so use the CLI:

```bash
cd rosal-ai
npx wrangler login
npx wrangler pages deploy . --project-name rosal-ai
```

Then do step 5 and 6 above (add the `AI` binding in the dashboard, redeploy the same command).

## Test locally

```bash
npx wrangler pages dev . --ai=AI
```

Note: Workers AI counts against your quota even in local development.

## Customize

- Personality: edit `SYSTEM_PROMPT` in `functions/api/chat.js`.
- Model: change `MODEL` in the same file to any chat model from the Workers AI catalog
  (https://developers.cloudflare.com/workers-ai/models/). Models get renamed or retired
  over time, so if you see "model unavailable" and your quota isn't used up, check the catalog.
- Colors: the `:root` variables at the top of `index.html`.
- Custom domain: Pages project -> Custom domains (the domain itself costs money; the
  hosting stays free).

## Protect your quota

Because the URL is public, someone could burn your 10,000 daily Neurons. Options:
- Cloudflare dashboard -> Security -> WAF -> Rate limiting rules (free plan has a basic rule).
- Add a simple access password or login check inside `chat.js` before calling the model.
- Put the site behind Cloudflare Access (free for up to 50 users).

## Alternatives if you outgrow this

- Google Gemini API or Groq both offer free tiers with API keys; keep the key in a Pages
  environment variable (Settings -> Variables and Secrets), never in `index.html`.

---

# Streamlit version (Gemini)

Main file: `streamlit_app.py`. Dependencies: `requirements.txt`. Theme: `.streamlit/config.toml`.

## Run locally

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then put your key in it
streamlit run streamlit_app.py
```

Get a free key at https://aistudio.google.com (Get API key).

## Deploy free on Streamlit Community Cloud

1. Push this repo to GitHub (keep it private if you like).
2. Go to https://share.streamlit.io, sign in with GitHub and authorize access to the repo.
3. **Create app** -> pick the repo, branch `main`, main file path `streamlit_app.py`.
4. Open **Advanced settings -> Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "your-key"
   APP_PASSWORD = "choose-a-password"   # optional, recommended
   ```
5. Deploy. You get a `*.streamlit.app` address.

`APP_PASSWORD` stops strangers from using up your free Gemini quota. If the model name stops
working, set `GEMINI_MODEL` in Secrets to a current one (default: `gemini-3.8-flash`).
