# SAATHI — Project Brief

## Problem statement

**PS 09 — Improving Access to Trusted Safety Support**

SAATHI is intended to help people—especially women, adolescent girls, people with disabilities, and others seeking safety support—discover appropriate help, understand privacy choices, document public-space hazards, and navigate referrals without being pressured into making a formal complaint.

## User problems the project addresses

The prior project research identified related barriers:

1. People may not know which service fits their situation.
2. Reporting can feel risky when retaliation, job loss, or relationship consequences are possible.
3. Stigma and victim-blaming can discourage disclosure.
4. Users may not understand what information is collected or when it might be shared.
5. Reporting pathways can be difficult to navigate or may not communicate what happens next.
6. A directory listing does not guarantee a service is currently available or accessible.
7. Support may require coordination across counselling, legal assistance, medical services, or shelter.
8. Poor lighting, obstructed footpaths, isolated locations, and unsafe transport stops can create environmental concerns.
9. Risk may arise during the walk to transit, waiting, transfers, travel, or the final stretch.
10. Safety concerns can restrict access to education, work, and public life.
11. Adolescent girls and people with disabilities may need more specific safeguarding and accessibility support.
12. Emotional support may be needed after the immediate incident.

The research material included government service descriptions, news reporting, research articles, and local safety audits. These sources document different types of evidence and must not be treated as one nationwide prevalence estimate.

## Product response

- **Smart Support Finder:** search a directory by keyword and category.
- **Community Safety Reporting:** submit specific environmental hazards with a text location and optional coordinates.
- **Private Support Preferences:** explore support categories and save a preference without automatically contacting a provider.
- **Emergency information:** display relevant emergency contact pathways with clear warnings that the website is not monitored for emergencies.
- **Accessible, privacy-conscious interface:** use clear language, minimize unnecessary collection, and explain what the demo stores.

## Current prototype scope

The starter implementation includes a responsive four-view web UI, a FastAPI REST API, SQLite persistence through SQLAlchemy, seeded demo service listings, hazard submission/listing, support preference submission, and automated API tests.

The prototype does **not** include live emergency dispatch, real-time safe-route scoring, AI-based risk assessment, authenticated caseworker access, automatic referrals, or confirmed external service integrations. Demo service entries are marked unverified. A submitted report is saved locally and is not sent to authorities.

## Safety principles

- Do not promise absolute anonymity or confidentiality.
- Do not treat AI as a judge of whether an incident is truthful.
- Do not claim a route is safe merely because it has more data.
- Verify service details and availability before deployment.
- Add authentication, access control, moderation, retention limits, and a formal security/privacy review before handling real sensitive cases.
