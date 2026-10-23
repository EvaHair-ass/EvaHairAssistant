import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';

export function openDb(dataDir) {
  mkdirSync(dataDir, { recursive: true });
  const db = new DatabaseSync(join(dataDir, 'niches.db'));
  db.exec(`
    CREATE TABLE IF NOT EXISTS reports (
      id         TEXT PRIMARY KEY,
      owner      TEXT NOT NULL,
      niche      TEXT NOT NULL,
      report     TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS reports_owner ON reports (owner, created_at DESC);
  `);

  const insert = db.prepare('INSERT INTO reports (id, owner, niche, report, created_at) VALUES (?, ?, ?, ?, ?)');
  const list = db.prepare('SELECT id, niche, created_at FROM reports WHERE owner = ? ORDER BY created_at DESC');
  const get = db.prepare('SELECT id, niche, report, created_at FROM reports WHERE id = ? AND owner = ?');
  const remove = db.prepare('DELETE FROM reports WHERE id = ? AND owner = ?');

  return {
    save(owner, report) {
      const row = { id: randomUUID(), createdAt: new Date().toISOString() };
      insert.run(row.id, owner, report.niche, JSON.stringify(report), row.createdAt);
      return { id: row.id, niche: report.niche, createdAt: row.createdAt };
    },
    list: (owner) => list.all(owner).map((r) => ({ id: r.id, niche: r.niche, createdAt: r.created_at })),
    get(owner, id) {
      const r = get.get(id, owner);
      return r && { id: r.id, niche: r.niche, createdAt: r.created_at, report: JSON.parse(r.report) };
    },
    delete: (owner, id) => remove.run(id, owner).changes > 0,
    close: () => db.close(),
  };
}
