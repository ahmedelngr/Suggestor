-- Real accounts (decided for MVP1): name + phone, plus email/password for login and reset.
-- Phone is personal data: keep it in `users` only; never export it to ml/ or data/.
ALTER TABLE users
    ADD COLUMN first_name    TEXT,
    ADD COLUMN last_name     TEXT,
    ADD COLUMN phone         TEXT,              -- collected, not SMS-verified in MVP1
    ADD COLUMN password_hash TEXT,              -- bcrypt/argon2 hash only, never plaintext
    ADD COLUMN onboarded_at  TIMESTAMPTZ;       -- set when the onboarding screening is finished

-- Items shown in the sign-up screening. Chosen to span cuisines and price tiers.
ALTER TABLE items ADD COLUMN is_onboarding_seed BOOLEAN NOT NULL DEFAULT false;
CREATE INDEX items_onboarding_seed_idx ON items (id) WHERE is_onboarding_seed;
