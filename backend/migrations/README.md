# Database Migrations

This directory contains SQL migration scripts for the idol_private database.

## Running Migrations

### Option 1: Using the Migration Script (Recommended)

```bash
cd backend/migrations
./run_migrations.sh
```

### Option 2: Manual Execution

```bash
# Make sure PostgreSQL is running and database exists
psql -h localhost -p 5432 -U idol_user -d idol_db -f 002_create_idols_table.sql
```

### Option 3: Using Docker Exec (if using Docker Compose)

```bash
docker exec -i idol_postgres psql -U idol_user -d idol_db < backend/migrations/002_create_idols_table.sql
```

## Migration Files

- `002_create_idols_table.sql` - Creates idols table and inserts first idol (林雪晴)

## Verify Migration

After running migrations, verify the data:

```bash
psql -h localhost -p 5432 -U idol_user -d idol_db -c "SELECT * FROM idols;"
```

Expected output:
```
 id |  name   |          avatar_url           | ... | is_active
----+---------+-------------------------------+-----+-----------
  1 | 林雪晴  | /assets/avatars/lin_xueqing.png | ... |     t
```

## Environment Variables

The migration script uses the following environment variables (default values shown):

- `DB_HOST=localhost`
- `DB_PORT=5432`
- `DB_NAME=idol_db`
- `DB_USER=idol_user`
- `DB_PASSWORD=idol_password`

These can be set in `backend/.env` file.
