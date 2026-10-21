-- Embedding dimension 384 matches all-MiniLM-L6-v2. Changing the model means a new migration.
CREATE EXTENSION IF NOT EXISTS vector;

-- Generic items table: restaurants now; events/hotels later without redesign.
CREATE TABLE items (
    id            BIGSERIAL PRIMARY KEY,
    type          TEXT NOT NULL,              -- 'restaurant', later 'event', 'hotel'
    source        TEXT NOT NULL,              -- 'yelp', 'google', ...
    source_id     TEXT NOT NULL,
    title         TEXT NOT NULL,
    description   TEXT,
    latitude      DOUBLE PRECISION,
    longitude     DOUBLE PRECISION,
    price_tier    SMALLINT CHECK (price_tier BETWEEN 1 AND 4),
    tags          TEXT[] NOT NULL DEFAULT '{}',
    image_url     TEXT,
    embedding     vector(384),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, source_id)
);

CREATE INDEX items_embedding_idx ON items USING hnsw (embedding vector_cosine_ops);
CREATE INDEX items_type_idx ON items (type);

CREATE TABLE users (
    id           BIGSERIAL PRIMARY KEY,
    email        TEXT UNIQUE,
    taste_vector vector(384),                 -- same dimension as items.embedding
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Append-only log: never UPDATE or DELETE rows. Source of truth for training and eval.
CREATE TABLE swipes (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(id),
    item_id    BIGINT NOT NULL REFERENCES items(id),
    liked      BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX swipes_user_time_idx ON swipes (user_id, created_at DESC);
CREATE INDEX swipes_user_item_idx ON swipes (user_id, item_id, created_at DESC);

-- Latest swipe per (user, item): "latest signal wins" for taste-vector math.
CREATE VIEW latest_swipes AS
SELECT DISTINCT ON (user_id, item_id) user_id, item_id, liked, created_at
FROM swipes
ORDER BY user_id, item_id, created_at DESC;

-- Guard the append-only rule at the database level.
CREATE FUNCTION swipes_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'swipes is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER swipes_no_update_delete
BEFORE UPDATE OR DELETE ON swipes
FOR EACH ROW EXECUTE FUNCTION swipes_append_only();
