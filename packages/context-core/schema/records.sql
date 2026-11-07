-- The record model of context_core as PostgreSQL tables: the first schema of step 0, not used yet.
-- Step 2 fills these tables as the index of each root (a cache rebuilt from the folder); step 4 makes them the source.
-- Plain PostgreSQL only, so changing host is a dump and a restore (hosted-stack.md, «Rule for the database»).
--
-- Every table but organization carries org_id, and row-level security filters every table, organization included
-- (by its id), by the organization set in each transaction from the verified request (hosted-security.md, gap 3): the application role cannot bypass it, migrations run with another role.
-- Nested parts of a record that are always read with it (the Estatus, a decision reference) are jsonb; lists of names
-- are text[]. Names follow records.py; tests/test_schema.py fails if a record field has no column.

CREATE TABLE organization (
    id          uuid PRIMARY KEY,
    name        text NOT NULL,
    region      text NOT NULL DEFAULT 'us-central1',
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE root (
    org_id              uuid PRIMARY KEY REFERENCES organization (id),
    name                text NOT NULL,
    organization        text NOT NULL DEFAULT '',
    method_line         text NOT NULL DEFAULT '',
    method_version      integer[],
    method_fingerprint  text,
    language            text NOT NULL DEFAULT 'es',      -- the root's language pack (language.py)
    timezone            text NOT NULL DEFAULT 'America/Mexico_City',
    context_owner       text NOT NULL DEFAULT '',
    administrator       text NOT NULL DEFAULT '',
    warnings            text[] NOT NULL DEFAULT '{}'
);

CREATE TABLE person (
    org_id          uuid NOT NULL REFERENCES organization (id),
    position        integer NOT NULL,                -- line order in «Quién es quién»
    name            text NOT NULL,
    accounts        text[] NOT NULL DEFAULT '{}',
    drive_accounts  text[] NOT NULL DEFAULT '{}',
    no_account      boolean NOT NULL DEFAULT false,
    unconfirmed     boolean NOT NULL DEFAULT false,
    aliases         text[] NOT NULL DEFAULT '{}',
    organization    text NOT NULL DEFAULT '',
    left_on         text NOT NULL DEFAULT '',
    shared_with     text NOT NULL DEFAULT '',
    registered_by   text NOT NULL DEFAULT '',
    PRIMARY KEY (org_id, position)
);

CREATE TABLE area_row (
    org_id                 uuid NOT NULL REFERENCES organization (id),
    slug                   text NOT NULL,
    what                   text NOT NULL DEFAULT '',
    responsible            text NOT NULL DEFAULT '',
    responsible_accounts   text[] NOT NULL DEFAULT '{}',
    collaborators          text[] NOT NULL DEFAULT '{}',
    collaborator_accounts  text[] NOT NULL DEFAULT '{}',
    readers                text NOT NULL DEFAULT '',
    access                 text NOT NULL DEFAULT '',
    restricted             boolean NOT NULL DEFAULT true,   -- fail closed
    warnings               text[] NOT NULL DEFAULT '{}',
    PRIMARY KEY (org_id, slug)
);

CREATE TABLE premise (
    org_id        uuid NOT NULL REFERENCES organization (id),
    id            text NOT NULL,
    text          text NOT NULL,
    line          text NOT NULL,
    confirmed_by  text NOT NULL DEFAULT '',
    date          text NOT NULL DEFAULT '',
    replaces      text,
    PRIMARY KEY (org_id, id)
);

CREATE TABLE area (
    org_id       uuid NOT NULL REFERENCES organization (id),
    slug         text NOT NULL,
    restricted   boolean NOT NULL DEFAULT false,
    state        text,
    updated      text,
    title        text NOT NULL DEFAULT '',
    what         text NOT NULL DEFAULT '',
    status       jsonb,                                -- records.Status
    priorities   text[] NOT NULL DEFAULT '{}',
    responsible  text NOT NULL DEFAULT '',
    PRIMARY KEY (org_id, slug)
);

CREATE TABLE index_entry (
    org_id        uuid NOT NULL REFERENCES organization (id),
    area          text NOT NULL,
    slug          text NOT NULL,
    description   text NOT NULL DEFAULT '',
    restricted    boolean NOT NULL DEFAULT false,
    deliverables  jsonb NOT NULL DEFAULT '{}',         -- stem -> {"description", "updated"}
    notes         text[] NOT NULL DEFAULT '{}',
    PRIMARY KEY (org_id, area, slug)
);

CREATE TABLE project (
    org_id         uuid NOT NULL REFERENCES organization (id),
    area           text NOT NULL,
    slug           text NOT NULL,
    restricted     boolean NOT NULL DEFAULT false,
    state          text,
    updated        text,
    title          text NOT NULL DEFAULT '',
    objective      text NOT NULL DEFAULT '',
    done_means     text NOT NULL DEFAULT '',
    scope          text NOT NULL DEFAULT '',
    status         jsonb,                              -- records.Status
    responsible    text NOT NULL DEFAULT '',
    collaborators  text[] NOT NULL DEFAULT '{}',
    consumers      text NOT NULL DEFAULT '',
    PRIMARY KEY (org_id, area, slug)
);

CREATE TABLE step (
    org_id    uuid NOT NULL REFERENCES organization (id),
    area      text NOT NULL,
    project   text NOT NULL,
    position  integer NOT NULL,
    text      text NOT NULL,
    dates     text[] NOT NULL DEFAULT '{}',
    PRIMARY KEY (org_id, area, project, position)
);

CREATE TABLE decision (
    org_id                uuid NOT NULL REFERENCES organization (id),
    area                  text NOT NULL,
    project               text NOT NULL,
    position              integer NOT NULL,          -- order in the register, newest first; entries never change
    id                    text NOT NULL DEFAULT '',  -- AAAA-MM-DD[-n]; '' when the heading has no valid date
    date                  text NOT NULL DEFAULT '',
    title                 text NOT NULL,
    decided_by            text NOT NULL DEFAULT '',
    why                   text NOT NULL DEFAULT '',
    discarded             text NOT NULL DEFAULT '',
    affects               text NOT NULL DEFAULT '',
    raised_by             text NOT NULL DEFAULT '',
    challenges            jsonb,                     -- records.DecisionRef
    responds_to           jsonb,
    replaces              jsonb,
    pending_confirmation  boolean NOT NULL DEFAULT false,
    kind                  text NOT NULL DEFAULT 'decision' CHECK (kind IN ('decision', 'challenge')),
    archived              boolean NOT NULL DEFAULT false,
    PRIMARY KEY (org_id, area, project, position)
);

CREATE TABLE session_entry (
    org_id          uuid NOT NULL REFERENCES organization (id),
    area            text NOT NULL,
    project         text NOT NULL,
    n               integer NOT NULL,                -- position from the oldest entry
    date            text NOT NULL DEFAULT '',
    title           text NOT NULL,
    topic           text NOT NULL DEFAULT '',
    progress        text NOT NULL DEFAULT '',
    pending         text NOT NULL DEFAULT '',
    by_name         text NOT NULL DEFAULT '',        -- records.SessionEntry.by
    plugin_version  text NOT NULL DEFAULT '',
    server_version  text NOT NULL DEFAULT '',
    wrote           text[] NOT NULL DEFAULT '{}',
    published       text[] NOT NULL DEFAULT '{}',
    archived        boolean NOT NULL DEFAULT false,
    PRIMARY KEY (org_id, area, project, n)
);

CREATE TABLE deliverable (
    org_id             uuid NOT NULL REFERENCES organization (id),
    area               text NOT NULL,
    project            text NOT NULL,
    file               text NOT NULL,
    name               text NOT NULL,
    format             text NOT NULL DEFAULT '',
    title              text,
    state              text,
    updated            text,
    based_on           text[] NOT NULL DEFAULT '{}',
    replaced_by        text,
    contribution       text,
    description        text NOT NULL DEFAULT '',
    PRIMARY KEY (org_id, area, project, file)
);

CREATE TABLE workshop_file (
    org_id   uuid NOT NULL REFERENCES organization (id),
    area     text NOT NULL,
    project  text NOT NULL,
    path     text NOT NULL,
    title    text,
    updated  text,
    PRIMARY KEY (org_id, area, project, path)
);

-- Tenant isolation: each transaction runs SET LOCAL app.org_id = '<uuid>' from the verified request.
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['root', 'person', 'area_row', 'premise', 'area', 'index_entry', 'project', 'step',
                             'decision', 'session_entry', 'deliverable', 'workshop_file'] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
        EXECUTE format('CREATE POLICY tenant ON %I USING (org_id = current_setting(''app.org_id'')::uuid) '
                       'WITH CHECK (org_id = current_setting(''app.org_id'')::uuid)', t);
    END LOOP;
END $$;
ALTER TABLE organization ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant ON organization USING (id = current_setting('app.org_id')::uuid)
    WITH CHECK (id = current_setting('app.org_id')::uuid);
-- Finding the organization of a verified account happens before app.org_id is set: it belongs to a separate lookup with
-- its own role (step 1), never to the application role.
