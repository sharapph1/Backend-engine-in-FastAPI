# WebX Cloudflare Worker API

This is a Workers-native replacement for the FastAPI/Render runtime. It keeps
the current Supabase PostgreSQL schema and data intact by connecting through a
Cloudflare Hyperdrive binding. It does not use D1 and it does not proxy to
Render.

## Required one-time setup

1. In Supabase, obtain the **Direct connection** URI from Database Settings.
   Do not use the Supabase pooler URI: Hyperdrive performs the pooling.
2. Create the Hyperdrive configuration without committing the connection URI:

   ```powershell
   npx wrangler hyperdrive create webx-supabase --connection-string="postgres://USER:PASSWORD@HOST:5432/postgres"
   ```

3. Copy the returned ID into the `HYPERDRIVE` entry in `wrangler.jsonc`, in
   place of `REPLACE_WITH_HYPERDRIVE_ID`.
4. Set Workers secrets. Reuse the same JWT secret value currently used by the
   Python service so existing access/refresh tokens remain valid:

   ```powershell
   npx wrangler secret put JWT_SECRET_KEY
   npx wrangler secret put BREVO_API_KEY
   npx wrangler secret put BREVO_FROM_EMAIL
   ```

   `BREVO_API_KEY` is a Brevo v3 HTTP API key. Workers cannot use the existing
   SMTP credentials directly. Set `R2_PUBLIC_URL` in `wrangler.jsonc` to the
   public URL/custom domain of the existing `webx-assets` bucket.
5. Install and validate the Worker:

   ```powershell
   npm install
   npm run check
   npm run deploy
   ```

After successful validation, remove the obsolete proxy setting, if present:

```powershell
npx wrangler secret delete API_ORIGIN
```

## Important compatibility notes

- Existing PostgreSQL tables, user records, Argon2id password hashes, JWTs,
  R2 object URLs, and `/api/v1` routes are retained.
- This code uses `@noble/hashes` to verify and generate the same Argon2id PHC
  format used by `pwdlib` in the Python backend.
- Avatar validation and R2 upload are retained. The original center-crop and
  WebP re-encoding require an image-processing service such as Cloudflare
  Images; base Workers cannot decode and encode all supplied image formats.
