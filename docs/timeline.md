# Timeline (proposed, lead to edit)

8 weeks, Oct 12 to Dec 4, with buffer around Thanksgiving. We are already past the start; treat weeks as sequential blocks and shift dates if needed.

| Week | Data | Modeling + Testing | Backend | Frontend |
|---|---|---|---|---|
| 1 | Yelp viability memo | Eval harness design | Local setup, migrations | Expo skeleton on phone |
| 2 | Ingestion script | Eval harness + baselines | Auth | Sign-up/login screens (mock API) |
| 3 | Cleaning, seed set | Training-pair rules | Swipes + taste vector | Onboarding screening |
| 4 | Data card, gaps fixed | Fine-tune v1 | Feed + search | Swipe card stack |
| 5 | Refresh data | Compare to baselines | Distance, cooldown config | Search, states |
| 6 | Support | Tune; weighting recommendation | Hardening, tests | Polish, attribution |
| 7 | Support | Final numbers | Deploy locally / demo setup | Demo build |
| 8 | Demo prep (Thanksgiving buffer applies) | | | |

## Cut line
If we fall behind, drop in this order: (1) two-tower stretch, (2) search polish, (3) distance ranking. Never drop: swipe log, taste vector, eval scoreboard.

## Milestones
- **M1 (end week 2):** data in the database; eval harness runs.
- **M2 (end week 4):** end-to-end loop: sign up, onboard, swipe, see a feed.
- **M3 (end week 6):** fine-tuned model beats or honestly fails to beat baselines.
- **M4 (week 8):** demo.
