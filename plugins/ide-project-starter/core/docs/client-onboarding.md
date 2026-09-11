# Client-folder onboarding

Version-Timestamp: 2026-09-08T21:58:13.941045-04:00
Status: v0.3 supervised client workflow. No background wizard or autonomous observer.

## User flow

Keep the existing company/client/project folder layout. Open the client folder, invoke project-starter, state the intended project and supply the repository URL if relevant. The installed plugin should make this skill available there; source-checkout users can explicitly point the agent to skills/project-starter/SKILL.md. Do not assume source-checkout skills are globally installed.

The conversational wizard proceeds through discovery, project selection, understanding, setup preview, initialization/adoption, source subscription and checkpoint. It asks missing questions after inspecting available context. For daily work, open the project folder; when staying at the client root, explicitly choose the project before each change.

## Discovery and coverage

Run the trusted helper, substituting the resolved toolkit and client paths:

```sh
python3 -B TOOLKIT/scripts/project_client.py --root CLIENT inventory
```

Inventory reads filenames and bounded project.json identity metadata only. It never selects a project. Hidden/secret locations, symlinks and nested clients are skipped. The default scan examines at most 500 entries; truncation is a gap, not complete coverage. Filenames are confidential too. Keep the output in the authorized workspace and minimize what enters chat/review packets.

The agent then reads only selected relevant documents with appropriate available tools. Create an understanding report with objective, audience, constraints, authoritative sources, assumptions, contradictions, missing inputs and first milestone. Record each source as read, partially read, inaccessible, requires extraction or excluded, plus reader/date. A file listing is not understanding. A transcript statement is not automatically an approved decision. Google Drive pointers require authorized retrieval; unreadable sources remain explicit gaps.

Before writing internal summaries, establish whether the destination is shared and who can access it. A subfolder name and .gitignore do not change Drive permissions. If sharing is unknown, ask for the correct destination rather than assuming privacy. Never upload contacts/transcripts as a default Git backup set.

## Identity and project choice

After client metadata creation is authorized:

```sh
python3 -B TOOLKIT/scripts/project_client.py --root CLIENT init --name "Client name" --sharing unknown
```

Use internal or shared only from confirmed user information. This writes CLIENT.json once and preserves its random UUID. It does not verify provider ACLs. Existing name/classification differences require review. Copying/restoring a client preserves its logical identity; a different client must get a newly initialized root. No global duplicate-identity registry exists, and copied UUIDs are not authentication.

Choose an existing project by its project.json identity, or create the requested project folder. Do not initialize Git at the client root. Preserve nested repositories, remotes and uncommitted work. Existing collisions follow intake.md; use adopt-existing.md for reviewed additive integration and exact instruction appends. General semantic merging is not automated.

## Initialization environment and preview

Use a Python environment with experiments/requirements.lock.txt from the trusted toolkit. For a plugin with no existing tested environment, an authorized local setup can use:

```sh
python3 -m venv CLIENT/.starter-tools/env
CLIENT/.starter-tools/env/bin/python -m pip install -r TOOLKIT/experiments/requirements.lock.txt
```

The environment is local to the selected client workspace, excluded from Git and still subject to Drive sync. For shared folders choose an approved tooling workspace instead. No credentials belong there. The plugin itself stays unchanged. Package pins require network access and are not hash-locked or vulnerability-certified.

Prepare the six-field brief from QUICKSTART or STARTER-CLI (name, profile, objective, audience, constraints, success_criteria), using relative paths inside the selected workspace:

```sh
PYTHON TOOLKIT/scripts/start_project.py --workspace CLIENT preview --target Projects/website --input website-input.json --plan website-plan.json
PYTHON TOOLKIT/scripts/start_project.py --workspace CLIENT apply --plan website-plan.json
```

Preview stops on conflicts and writes only its plan/scratch, not project files. Workspace scratch lives in .starter-work/render. Every project gets its own memory, identity, skills and helper copies. Client source files stay in place.

## Link reviewed shared context

From the generated project root, create a source-selection.json containing exactly a sources list of client-relative text paths, for example `{"sources":["Client Context/brief.md"]}`. Use reviewed summaries when raw material is too sensitive. Selection reads the chosen text to check size/encoding and selected secret patterns, but records only paths and SHA-256 hashes. It is not a complete PII or credential classifier.

```sh
python3 -B .starter/project_client.py --root . link --client-root CLIENT --input source-selection.json --expected-head none
python3 -B .starter/project_client.py --root . status
python3 -B .starter/project_memory.py resume
```

Only sources inside the identified client ancestor are allowed. Sources inside another project or nested client are refused. Current support is bounded UTF-8 text (1 MiB/file), not raw binary documents. Approved text extraction remains separate. Track raw-source changes in the source register until an extraction freshness adapter exists.

A project subscribes only to its selected shared files. Changes trigger needs_review on resume; hashes are never silently advanced. For a reviewed refresh, run status to obtain the current head, then link again with that head and the new reviewed selection. A numbered immutable revision preserves the old association. Link history is project-specific and serialized; a conflicting writer fails without overwrite.

Moving the entire client tree preserves ancestor-relative associations. Moving only the project reports unavailable until explicitly reconciled. Client identity mismatch prevents reading selected sources. These are continuity checks, not access control or signatures. Same-user malicious filesystem replacement, hardlink aliasing and distributed sync races are outside the pilot's protection.

## Handoff

Complete the project context register and real quality requirements, record source limitations and saved client-link revision, then checkpoint the actual work. Resume must report project state and client-context freshness. Keep accepted client facts, project decisions and raw sources distinct.

Initializers and client helpers make no Git/network calls. A future project's repository and upload scope need separate authorization. The kit's private repository backs up tooling, not all client source material.

On every resume and refresh, intervening client, project and Git boundaries are checked again. A newly inserted boundary makes the link unavailable until explicitly reconciled. A missing client helper during a partial upgrade makes resume require review. Unsafe, empty or invalid changed text remains flagged and cannot be accepted simply by refreshing its hash; reconcile the source first.

Resolve Start new, Adopt existing or Resume before applying a template. Record storage destinations and audiences per storage-boundaries.md. A cloud client folder is the discovery context; the chosen development/memory workspace may be elsewhere when permissions or sync make that preferable. Sources outside the client ancestor use references and approved snapshots, not implicit client-link subscriptions.
