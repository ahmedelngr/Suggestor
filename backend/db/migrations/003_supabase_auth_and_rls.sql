-- Supabase: link profiles to Supabase Auth and lock tables down with RLS.
-- Run in the Supabase SQL editor. Uses the `auth` schema, so it will NOT run on plain Postgres.

-- 1. Supabase Auth owns passwords. Link each profile to its auth user.
ALTER TABLE users DROP COLUMN password_hash;
ALTER TABLE users ADD COLUMN auth_id uuid UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE;

-- 2. Auto-create a profile row on sign-up. The app passes first_name, last_name, phone
--    as metadata: supabase.auth.signUp({ email, password, options: { data: { ... } } })
CREATE FUNCTION public.handle_new_user() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
    INSERT INTO public.users (auth_id, email, first_name, last_name, phone)
    VALUES (
        NEW.id, NEW.email,
        NEW.raw_user_meta_data->>'first_name',
        NEW.raw_user_meta_data->>'last_name',
        NEW.raw_user_meta_data->>'phone'
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 3. Helper: the profile id of the signed-in user.
CREATE FUNCTION public.current_user_id() RETURNS bigint
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
    SELECT id FROM public.users WHERE auth_id = auth.uid()
$$;

-- 4. Row Level Security: on, with no access by default.
ALTER TABLE items  ENABLE ROW LEVEL SECURITY;
ALTER TABLE users  ENABLE ROW LEVEL SECURITY;
ALTER TABLE swipes ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON items, users, swipes, latest_swipes FROM anon;

-- items: any signed-in user can read. Writes only via service key (Yelp script).
CREATE POLICY items_read ON items FOR SELECT TO authenticated USING (true);

-- users: each person sees and edits only their own row.
CREATE POLICY users_select_own ON users FOR SELECT TO authenticated
    USING (auth_id = auth.uid());
CREATE POLICY users_update_own ON users FOR UPDATE TO authenticated
    USING (auth_id = auth.uid()) WITH CHECK (auth_id = auth.uid());

-- swipes: read and insert only your own. No update or delete (a trigger also blocks them).
CREATE POLICY swipes_select_own ON swipes FOR SELECT TO authenticated
    USING (user_id = public.current_user_id());
CREATE POLICY swipes_insert_own ON swipes FOR INSERT TO authenticated
    WITH CHECK (user_id = public.current_user_id());

-- 5. The view must obey the caller's RLS, or it leaks everyone's swipes.
ALTER VIEW latest_swipes SET (security_invoker = true);
