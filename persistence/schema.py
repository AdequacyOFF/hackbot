SCHEMA_SQL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS competitions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  sponsor TEXT,
  dates_text TEXT NOT NULL,
  format TEXT NOT NULL,
  link TEXT,
  description TEXT DEFAULT '',
  end_date TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS teams(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  competition_id INTEGER NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  member_count INTEGER NOT NULL,
  captain_index INTEGER NOT NULL,
  location TEXT NOT NULL,
  curator TEXT NOT NULL,
  user_id INTEGER,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS members(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  ordinal INTEGER NOT NULL,
  rank TEXT NOT NULL,
  fio TEXT NOT NULL,
  study_group TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS results(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  competition_id INTEGER NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
  team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  place INTEGER NOT NULL,
  presentation_path TEXT,
  repo_url TEXT,
  comment TEXT,
  submitted_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS suggestions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  sponsor TEXT NOT NULL,
  dates_text TEXT NOT NULL,
  format TEXT NOT NULL,
  link TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_results_comp ON results(competition_id);
CREATE INDEX IF NOT EXISTS idx_teams_comp ON teams(competition_id);
"""