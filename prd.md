1. Syfte

Automatisera framtagning av kredit-PM för företag, genom att kombinera:

Publika bolagsdata (Bolagsverket, hemsidor).

Kommersiella riskdata (UC/D&B – POC kan använda dummy).

Makrodata (t.ex. STIBOR).

AI-generering (RAG + prognoser).
Målet är att banktjänstemän får ett PM-utkast som kan redigeras och exporteras som Word/PDF.

2. Målgrupp

Primär: Kundansvariga banktjänstemän.

Ej scope: Kunder (ingen extern inloggning).

3. Funktionella krav

3.1 Ärenden

Skapa nytt PM genom att ange organisationsnummer.

Systemet hämtar data (Bolagsverket API → företagsnamn, verksamhetsbeskrivning).

Ärendet sparas i Supabase med status + versionsnummer.

3.2 Sektioner (AI-stöd)

Syfte med PM: Redigerbart fält.

Affärsbeskrivning: RAG-sammanfattning (bolagsbeskrivning + hemside-crawls).

Marknad & konkurrenter: AI-utkast baserat på branschdata (POC: dummytexter).

Finansiell analys:

Inmatning eller API-hämtning av historiska siffror.

Prognosmodul (LightGBM/Prophet).

AI skriver texten.

Kreditanalys: AI föreslår riskklass utifrån bransch + finanser (UC/D&B om tillgängligt).

Kreditförslag: Policy-engine (hårda regler) + AI-motivering (mjuka delar).

3.3 Redigering

Inline-editor per sektion.

Ändringar autosparas till Supabase.

Versionshantering: handläggaren kan se diff mellan AI-utkast och redigerad version.

3.4 Export

Exportera hela PM som Word/PDF.

Sidfot innehåller datakällor, datum, modellversion.

3.5 Audit

Alla AI-outputs + prompts loggas i Supabase.

Versionsnummer per PM + per sektion.

Modellversion och datakällor lagras.

4. Icke-funktionella krav

Språk: Engelska (internbank).

Säkerhet (MVP): Supabase auth (email/pass eller SSO); row-level security på ärenden.

Testbarhet: Allt ska gå att köra lokalt via Docker Compose.

Deploybarhet:

Frontend på Netlify.

Backend på Node/FastAPI backend på Railway/Render.

Databas i Supabase Postgres.

5. Tech-stack (MVP)
   Frontend

Framework: Next.js (React, TypeScript).

UI-kit: shadcn/ui + Tailwind.

State management: TanStack Query.

Deployment: Netlify (enkel push-to-deploy).

Backend

FastAPI (Python) eller Node/Express backend på Railway.

Passar om du vill köra lokala ML-modeller (LightGBM/Prophet).

Database

Supabase (Postgres + pgvector).

companies (grunddata från BV).

financials (år, siffror).

pm_sections (sektionstext, AI-utkast, user-edited version, version_id).

audit_log (prompt, model_version, timestamp).

users (RBAC).

AI-lager

LLM-tjänst: OpenAI API (snabb prototyp) eller Anthropic.

RAG: pgvector (lagra embeddings för hemside-texter, verksamhetsbeskrivning).

Finansiell prognos: Python (pandas, LightGBM, Prophet) i backend.

Policy-engine: Enkel regelmotor i Python (POC), kan senare bytas till OPA.

Dokumentexport

Backend: python-docx + reportlab för PDF.

Alternativ: Templated docx som fylls med data.

Lokal utveckling

Docker Compose:

Next.js (frontend).

FastAPI/Node backend.

Supabase (lokal Postgres + Studio).

Hot reload i både frontend och backend.

6. Dataflöde (MVP)

Handläggare anger org.nr.

Backend anropar Bolagsverket API → returnerar bolagsdata → sparas i Supabase.

AI genererar “Affärsbeskrivning” och “Marknad” (dummy vid POC).

Handläggare laddar upp historiska siffror (Excel/CSV) → backend beräknar nyckeltal → AI genererar prognos-text.

Utkast sparas i pm_sections.

Handläggaren redigerar i UI → nya versioner sparas.

Slutlig PM exporteras till docx/pdf.

7. Roadmap

MVP:

Next.js UI + Supabase databas.

CRUD för PM.

AI-utkast för affärsbeskrivning (dummy RAG).

Inmatning av finanser + prognos (basmodell).

Export till PDF/Word.

Steg 2:

Integration mot UC/D&B (mock först).

Scenarioanalys (bas/låg/hög).

Policy-engine för kreditförslag.

Steg 3:

RAG på bolagshemsidor.

Automatisk marknadsanalys (branschdata).

Full audit-dashboard (modellversioner, användningsstatistik).

8. User Stories (exempel för backlog)

Som kundansvarig vill jag kunna ange ett org.nr och automatiskt få bolagsfakta i mitt PM så att jag slipper slå upp manuellt.

Som kundansvarig vill jag kunna ladda upp en Excel med historiska finanser så att systemet räknar nyckeltal och prognoser.

Som kundansvarig vill jag kunna se AI:s textförslag i varje sektion och redigera direkt i UI.

Som kundansvarig vill jag kunna exportera ett färdigt PM till Word med bankens standardmall.
